from dataclasses import FrozenInstanceError
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from businesses.models import Business
from catalog.forms import ProductChoiceForm, ProductChoiceFormSet, ProductForm
from catalog.models import (
    BusinessProductType,
    BusinessProductTypeAlias,
    BusinessTag,
    BusinessTagAlias,
    Product,
    ProductChoice,
    ProductMaterialFact,
)
from catalog.product_bundles import ProductBundle
from catalog.recognition import (
    RecognitionTerm,
    SemanticDestination,
    choice_suggestion_terms,
    material_terms_for_business,
    recognize_choice_suggestions,
    recognize_materials_for_business,
    recognize_tags_for_business,
    recognize_product_types_for_business,
    recognize_product_description,
)


class RecognitionServiceContractTests(SimpleTestCase):
    def test_recognition_preserves_observed_text_without_confirming_facts(self):
        description = "კლასიკური შარვალი, M-ზომა, ბამბა."
        terms = (
            RecognitionTerm(
                destination=SemanticDestination.PRODUCT_TYPE,
                canonical_value="შარვალი",
            ),
            RecognitionTerm(
                destination=SemanticDestination.MATERIAL,
                canonical_value="ბამბა",
            ),
        )

        result = recognize_product_description(description, terms=terms)

        self.assertEqual(result.observed_text, description)
        self.assertEqual(result.confirmed_facts, ())
        self.assertEqual(len(result.candidates), 2)
        self.assertTrue(
            all(candidate.requires_confirmation for candidate in result.candidates)
        )
        self.assertFalse(any(candidate.is_confirmed for candidate in result.candidates))

    def test_recognition_returns_transient_candidates_from_supplied_terms(self):
        description = "კლასიკური შარვალი ჯიბეებით, M-ზომა."
        terms = (
            RecognitionTerm(
                destination=SemanticDestination.PRODUCT_TYPE,
                canonical_value="შარვალი",
                aliases=("pants",),
            ),
            RecognitionTerm(
                destination=SemanticDestination.TAG,
                canonical_value="ჯიბეები",
                aliases=("ჯიბეებით",),
            ),
            RecognitionTerm(
                destination=SemanticDestination.CHOICE_SIZE,
                canonical_value="M",
            ),
        )

        result = recognize_product_description(description, terms=terms)

        self.assertEqual(
            [
                (candidate.destination, candidate.canonical_value)
                for candidate in result.candidates
            ],
            [
                (SemanticDestination.PRODUCT_TYPE, "შარვალი"),
                (SemanticDestination.TAG, "ჯიბეები"),
                (SemanticDestination.CHOICE_SIZE, "M"),
            ],
        )
        self.assertEqual(
            [candidate.observed_text for candidate in result.candidates],
            ["შარვალი", "ჯიბეებით", "M"],
        )

    def test_recognition_uses_only_caller_supplied_terms(self):
        description = "კლასიკური შარვალი"

        result_without_terms = recognize_product_description(description)
        result_with_terms = recognize_product_description(
            description,
            terms=(
                RecognitionTerm(
                    destination=SemanticDestination.PRODUCT_TYPE,
                    canonical_value="შარვალი",
                ),
            ),
        )

        self.assertEqual(result_without_terms.candidates, ())
        product_type_candidates = result_with_terms.candidates_for(
            SemanticDestination.PRODUCT_TYPE
        )
        self.assertEqual(
            product_type_candidates[0].canonical_value,
            "შარვალი",
        )

    def test_recognition_result_and_candidates_are_immutable(self):
        result = recognize_product_description(
            "ბამბა",
            terms=(
                RecognitionTerm(
                    destination=SemanticDestination.MATERIAL,
                    canonical_value="ბამბა",
                ),
            ),
        )

        with self.assertRaises(FrozenInstanceError):
            result.observed_text = "changed"
        with self.assertRaises(FrozenInstanceError):
            result.candidates[0].canonical_value = "changed"

    def test_empty_description_returns_no_candidates(self):
        result = recognize_product_description(
            "   ",
            terms=(
                RecognitionTerm(
                    destination=SemanticDestination.MATERIAL,
                    canonical_value="ბამბა",
                ),
            ),
        )

        self.assertEqual(result.observed_text, "   ")
        self.assertEqual(result.candidates, ())
        self.assertEqual(result.confirmed_facts, ())

    def test_negated_material_phrase_does_not_create_positive_candidate(self):
        result = recognize_product_description(
            "პოლიესტერი არ აქვს.",
            terms=(
                RecognitionTerm(
                    destination=SemanticDestination.MATERIAL,
                    canonical_value="პოლიესტერი",
                ),
            ),
        )

        self.assertEqual(result.candidates_for(SemanticDestination.MATERIAL), ())
        self.assertEqual(result.confirmed_facts, ())


class ChoiceSuggestionRecognitionTests(SimpleTestCase):
    def test_recognizes_supplied_size_and_color_as_choice_candidates(self):
        description = "M-ზომა, შავი ფერი."

        result = recognize_choice_suggestions(
            description,
            size_values=("M",),
            color_values=("შავი",),
        )

        self.assertEqual(result.observed_text, description)
        self.assertEqual(
            [
                (
                    candidate.destination,
                    candidate.canonical_value,
                    candidate.observed_text,
                )
                for candidate in result.candidates
            ],
            [
                (SemanticDestination.CHOICE_SIZE, "M", "M"),
                (SemanticDestination.CHOICE_COLOR, "შავი", "შავი"),
            ],
        )
        self.assertTrue(
            all(candidate.requires_confirmation for candidate in result.candidates)
        )
        self.assertFalse(any(candidate.is_confirmed for candidate in result.candidates))
        self.assertEqual(result.confirmed_facts, ())

    def test_choice_suggestions_without_supplied_values_returns_no_candidates(self):
        result = recognize_choice_suggestions("M-ზომა, შავი ფერი.")

        self.assertEqual(result.observed_text, "M-ზომა, შავი ფერი.")
        self.assertEqual(result.candidates, ())
        self.assertEqual(result.confirmed_facts, ())

    def test_choice_suggestion_terms_strip_and_dedupe_values(self):
        terms = choice_suggestion_terms(
            size_values=(" M ", "m", ""),
            color_values=(" შავი ", "შავი", " "),
        )

        self.assertEqual(
            [(term.destination, term.canonical_value) for term in terms],
            [
                (SemanticDestination.CHOICE_SIZE, "M"),
                (SemanticDestination.CHOICE_COLOR, "შავი"),
            ],
        )

    def test_choice_suggestions_are_not_generic_tags(self):
        result = recognize_choice_suggestions(
            "M ზომა და შავი ფერი",
            size_values=("M",),
            color_values=("შავი",),
        )

        self.assertEqual(result.candidates_for(SemanticDestination.TAG), ())
        self.assertEqual(len(result.candidates_for(SemanticDestination.CHOICE_SIZE)), 1)
        self.assertEqual(len(result.candidates_for(SemanticDestination.CHOICE_COLOR)), 1)
        self.assertEqual(result.confirmed_facts, ())

    def test_choice_suggestions_preserve_negation_boundary(self):
        result = recognize_choice_suggestions(
            "M არ აქვს.",
            size_values=("M",),
            color_values=("შავი",),
        )

        self.assertEqual(result.candidates_for(SemanticDestination.CHOICE_SIZE), ())
        self.assertEqual(result.candidates_for(SemanticDestination.CHOICE_COLOR), ())
        self.assertEqual(result.confirmed_facts, ())


class BusinessProductTypeModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="type-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="type-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )

    def test_product_type_belongs_to_business(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="შარვალი",
        )

        self.assertEqual(product_type.business, self.business)
        self.assertEqual(self.business.product_types.get(), product_type)

    def test_product_type_requires_business(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BusinessProductType.objects.create(name="Ownerless type")

    def test_product_type_requires_non_blank_name(self):
        for invalid_name in ("   ", None):
            with self.subTest(name=invalid_name):
                product_type = BusinessProductType(
                    business=self.business,
                    name=invalid_name,
                )

                with self.assertRaises(ValidationError):
                    product_type.full_clean()

    def test_product_type_name_is_case_insensitive_unique_per_business(self):
        BusinessProductType.objects.create(
            business=self.business,
            name=" Dress ",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BusinessProductType.objects.create(
                    business=self.business,
                    name="dress",
                )

    def test_product_type_name_is_stripped_on_save(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="  შარვალი  ",
        )

        self.assertEqual(product_type.name, "შარვალი")

    def test_same_product_type_name_can_exist_in_another_business(self):
        owned_type = BusinessProductType.objects.create(
            business=self.business,
            name="შარვალი",
        )
        other_type = BusinessProductType.objects.create(
            business=self.other_business,
            name="შარვალი",
        )

        self.assertNotEqual(owned_type.business, other_type.business)
        self.assertEqual(BusinessProductType.objects.count(), 2)

    def test_business_deletion_is_protected_when_product_type_exists(self):
        BusinessProductType.objects.create(
            business=self.business,
            name="შარვალი",
        )

        with self.assertRaises(ProtectedError):
            self.business.delete()

    def test_product_type_string_uses_name(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="შარვალი",
        )

        self.assertEqual(str(product_type), "შარვალი")


class BusinessTagModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="tag-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="tag-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )

    def test_tag_belongs_to_business(self):
        tag = BusinessTag.objects.create(
            business=self.business,
            name="ჯიბეები",
        )

        self.assertEqual(tag.business, self.business)
        self.assertEqual(self.business.tags.get(), tag)

    def test_tag_requires_business(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BusinessTag.objects.create(name="Ownerless tag")

    def test_tag_requires_non_blank_name(self):
        for invalid_name in ("   ", None):
            with self.subTest(name=invalid_name):
                tag = BusinessTag(
                    business=self.business,
                    name=invalid_name,
                )

                with self.assertRaises(ValidationError):
                    tag.full_clean()

    def test_tag_name_is_case_insensitive_unique_per_business(self):
        BusinessTag.objects.create(
            business=self.business,
            name=" Classic ",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BusinessTag.objects.create(
                    business=self.business,
                    name="classic",
                )

    def test_tag_name_is_stripped_on_save(self):
        tag = BusinessTag.objects.create(
            business=self.business,
            name="  ჯიბეები  ",
        )

        self.assertEqual(tag.name, "ჯიბეები")

    def test_same_tag_name_can_exist_in_another_business(self):
        owned_tag = BusinessTag.objects.create(
            business=self.business,
            name="ჯიბეები",
        )
        other_tag = BusinessTag.objects.create(
            business=self.other_business,
            name="ჯიბეები",
        )

        self.assertNotEqual(owned_tag.business, other_tag.business)
        self.assertEqual(BusinessTag.objects.count(), 2)

    def test_business_deletion_is_protected_when_tag_exists(self):
        BusinessTag.objects.create(
            business=self.business,
            name="ჯიბეები",
        )

        with self.assertRaises(ProtectedError):
            self.business.delete()

    def test_tag_string_uses_name(self):
        tag = BusinessTag.objects.create(
            business=self.business,
            name="ჯიბეები",
        )

        self.assertEqual(str(tag), "ჯიბეები")


class BusinessProductTypeAliasModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="type-alias-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="type-alias-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )
        self.product_type = BusinessProductType.objects.create(
            business=self.business,
            name="შარვალი",
        )
        self.other_product_type = BusinessProductType.objects.create(
            business=self.other_business,
            name="კაბა",
        )

    def test_product_type_alias_belongs_to_business_and_product_type(self):
        alias = BusinessProductTypeAlias.objects.create(
            business=self.business,
            product_type=self.product_type,
            alias="pants",
        )

        self.assertEqual(alias.business, self.business)
        self.assertEqual(alias.product_type, self.product_type)
        self.assertEqual(self.business.product_type_aliases.get(), alias)
        self.assertEqual(self.product_type.aliases.get(), alias)

    def test_product_type_alias_requires_business_and_product_type(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BusinessProductTypeAlias.objects.create(
                    product_type=self.product_type,
                    alias="pants",
                )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BusinessProductTypeAlias.objects.create(
                    business=self.business,
                    alias="pants",
                )

    def test_product_type_alias_requires_non_blank_alias(self):
        for invalid_alias in ("   ", None):
            with self.subTest(alias=invalid_alias):
                alias = BusinessProductTypeAlias(
                    business=self.business,
                    product_type=self.product_type,
                    alias=invalid_alias,
                )

                with self.assertRaises(ValidationError):
                    alias.full_clean()

    def test_product_type_alias_is_case_insensitive_unique_per_business(self):
        BusinessProductType.objects.create(
            business=self.business,
            name="კაბა",
        )
        BusinessProductTypeAlias.objects.create(
            business=self.business,
            product_type=self.product_type,
            alias=" Pants ",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BusinessProductTypeAlias.objects.create(
                    business=self.business,
                    product_type=self.product_type,
                    alias="pants",
                )

    def test_product_type_alias_is_stripped_on_save(self):
        alias = BusinessProductTypeAlias.objects.create(
            business=self.business,
            product_type=self.product_type,
            alias="  pants  ",
        )

        self.assertEqual(alias.alias, "pants")

    def test_same_product_type_alias_can_exist_in_another_business(self):
        owned_alias = BusinessProductTypeAlias.objects.create(
            business=self.business,
            product_type=self.product_type,
            alias="pants",
        )
        other_alias = BusinessProductTypeAlias.objects.create(
            business=self.other_business,
            product_type=self.other_product_type,
            alias="pants",
        )

        self.assertNotEqual(owned_alias.business, other_alias.business)
        self.assertEqual(BusinessProductTypeAlias.objects.count(), 2)

    def test_product_type_alias_requires_matching_business(self):
        alias = BusinessProductTypeAlias(
            business=self.business,
            product_type=self.other_product_type,
            alias="dress",
        )

        with self.assertRaises(ValidationError):
            alias.full_clean()
        with self.assertRaises(ValidationError):
            alias.save()

    def test_product_type_alias_cannot_match_canonical_type_name(self):
        BusinessProductType.objects.create(
            business=self.business,
            name="კაბა",
        )
        alias = BusinessProductTypeAlias(
            business=self.business,
            product_type=self.product_type,
            alias="კაბა",
        )

        with self.assertRaises(ValidationError):
            alias.full_clean()
        with self.assertRaises(ValidationError):
            alias.save()

    def test_product_type_name_cannot_match_existing_alias(self):
        BusinessProductTypeAlias.objects.create(
            business=self.business,
            product_type=self.product_type,
            alias="dress",
        )

        with self.assertRaises(ValidationError):
            BusinessProductType.objects.create(
                business=self.business,
                name="Dress",
            )

    def test_business_deletion_is_protected_when_product_type_alias_exists(self):
        BusinessProductTypeAlias.objects.create(
            business=self.business,
            product_type=self.product_type,
            alias="pants",
        )

        with self.assertRaises(ProtectedError):
            self.business.delete()

    def test_product_type_alias_string_uses_alias(self):
        alias = BusinessProductTypeAlias.objects.create(
            business=self.business,
            product_type=self.product_type,
            alias="pants",
        )

        self.assertEqual(str(alias), "pants")


class BusinessTagAliasModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="tag-alias-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="tag-alias-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )
        self.tag = BusinessTag.objects.create(
            business=self.business,
            name="ჯიბეები",
        )
        self.other_tag = BusinessTag.objects.create(
            business=self.other_business,
            name="კლასიკური",
        )

    def test_tag_alias_belongs_to_business_and_tag(self):
        alias = BusinessTagAlias.objects.create(
            business=self.business,
            tag=self.tag,
            alias="pockets",
        )

        self.assertEqual(alias.business, self.business)
        self.assertEqual(alias.tag, self.tag)
        self.assertEqual(self.business.tag_aliases.get(), alias)
        self.assertEqual(self.tag.aliases.get(), alias)

    def test_tag_alias_requires_business_and_tag(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BusinessTagAlias.objects.create(
                    tag=self.tag,
                    alias="pockets",
                )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BusinessTagAlias.objects.create(
                    business=self.business,
                    alias="pockets",
                )

    def test_tag_alias_requires_non_blank_alias(self):
        for invalid_alias in ("   ", None):
            with self.subTest(alias=invalid_alias):
                alias = BusinessTagAlias(
                    business=self.business,
                    tag=self.tag,
                    alias=invalid_alias,
                )

                with self.assertRaises(ValidationError):
                    alias.full_clean()

    def test_tag_alias_is_case_insensitive_unique_per_business(self):
        BusinessTag.objects.create(
            business=self.business,
            name="კლასიკური",
        )
        BusinessTagAlias.objects.create(
            business=self.business,
            tag=self.tag,
            alias=" Pockets ",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BusinessTagAlias.objects.create(
                    business=self.business,
                    tag=self.tag,
                    alias="pockets",
                )

    def test_tag_alias_is_stripped_on_save(self):
        alias = BusinessTagAlias.objects.create(
            business=self.business,
            tag=self.tag,
            alias="  pockets  ",
        )

        self.assertEqual(alias.alias, "pockets")

    def test_same_tag_alias_can_exist_in_another_business(self):
        owned_alias = BusinessTagAlias.objects.create(
            business=self.business,
            tag=self.tag,
            alias="pockets",
        )
        other_alias = BusinessTagAlias.objects.create(
            business=self.other_business,
            tag=self.other_tag,
            alias="pockets",
        )

        self.assertNotEqual(owned_alias.business, other_alias.business)
        self.assertEqual(BusinessTagAlias.objects.count(), 2)

    def test_tag_alias_requires_matching_business(self):
        alias = BusinessTagAlias(
            business=self.business,
            tag=self.other_tag,
            alias="classic",
        )

        with self.assertRaises(ValidationError):
            alias.full_clean()
        with self.assertRaises(ValidationError):
            alias.save()

    def test_tag_alias_cannot_match_canonical_tag_name(self):
        BusinessTag.objects.create(
            business=self.business,
            name="კლასიკური",
        )
        alias = BusinessTagAlias(
            business=self.business,
            tag=self.tag,
            alias="კლასიკური",
        )

        with self.assertRaises(ValidationError):
            alias.full_clean()
        with self.assertRaises(ValidationError):
            alias.save()

    def test_tag_name_cannot_match_existing_alias(self):
        BusinessTagAlias.objects.create(
            business=self.business,
            tag=self.tag,
            alias="classic",
        )

        with self.assertRaises(ValidationError):
            BusinessTag.objects.create(
                business=self.business,
                name="Classic",
            )

    def test_business_deletion_is_protected_when_tag_alias_exists(self):
        BusinessTagAlias.objects.create(
            business=self.business,
            tag=self.tag,
            alias="pockets",
        )

        with self.assertRaises(ProtectedError):
            self.business.delete()

    def test_tag_alias_string_uses_alias(self):
        alias = BusinessTagAlias.objects.create(
            business=self.business,
            tag=self.tag,
            alias="pockets",
        )

        self.assertEqual(str(alias), "pockets")


class ProductMaterialFactModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="material-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="material-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="შარვალი",
            description="100% ბამბა",
        )
        self.other_product = Product.objects.create(
            business=self.other_business,
            name="კაბა",
            description="ატლასი",
        )

    def test_material_fact_belongs_to_business_and_product(self):
        fact = ProductMaterialFact.objects.create(
            business=self.business,
            product=self.product,
            canonical_material="ბამბა",
            percentage=100,
            original_text="100% ბამბა",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )

        self.assertEqual(fact.business, self.business)
        self.assertEqual(fact.product, self.product)
        self.assertEqual(
            fact.confirmation_state,
            ProductMaterialFact.ConfirmationState.CONFIRMED,
        )
        self.assertEqual(self.business.product_material_facts.get(), fact)
        self.assertEqual(self.product.material_facts.get(), fact)

    def test_material_fact_requires_business_and_product(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductMaterialFact.objects.create(
                    product=self.product,
                    canonical_material="ბამბა",
                    original_text="ბამბა",
                    source=ProductMaterialFact.Source.DESCRIPTION,
                )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductMaterialFact.objects.create(
                    business=self.business,
                    canonical_material="ბამბა",
                    original_text="ბამბა",
                    source=ProductMaterialFact.Source.DESCRIPTION,
                )

    def test_material_fact_requires_non_blank_material_and_original_text(self):
        for field_name in ("canonical_material", "original_text"):
            with self.subTest(field_name=field_name):
                fact = ProductMaterialFact(
                    business=self.business,
                    product=self.product,
                    canonical_material="ბამბა",
                    original_text="ბამბა",
                    source=ProductMaterialFact.Source.DESCRIPTION,
                )
                setattr(fact, field_name, "   ")

                with self.assertRaises(ValidationError):
                    fact.full_clean()
                with self.assertRaises(ValidationError):
                    fact.save()

    def test_material_fact_strips_material_and_original_text_on_save(self):
        fact = ProductMaterialFact.objects.create(
            business=self.business,
            product=self.product,
            canonical_material="  ბამბა  ",
            original_text="  100% ბამბა  ",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )

        self.assertEqual(fact.canonical_material, "ბამბა")
        self.assertEqual(fact.original_text, "100% ბამბა")

    def test_material_fact_percentage_is_optional(self):
        fact = ProductMaterialFact.objects.create(
            business=self.business,
            product=self.product,
            canonical_material="ატლასი",
            original_text="ატლასი",
            source=ProductMaterialFact.Source.MANUAL,
        )

        self.assertIsNone(fact.percentage)

    def test_material_fact_rejects_invalid_percentage(self):
        for invalid_percentage in (0, 101):
            with self.subTest(percentage=invalid_percentage):
                fact = ProductMaterialFact(
                    business=self.business,
                    product=self.product,
                    canonical_material="ბამბა",
                    percentage=invalid_percentage,
                    original_text="ბამბა",
                    source=ProductMaterialFact.Source.DESCRIPTION,
                )

                with self.assertRaises(ValidationError):
                    fact.full_clean()
                with self.assertRaises(ValidationError):
                    fact.save()

    def test_material_fact_requires_known_source(self):
        for invalid_source in ("", "label_photo"):
            with self.subTest(source=invalid_source):
                fact = ProductMaterialFact(
                    business=self.business,
                    product=self.product,
                    canonical_material="ბამბა",
                    original_text="ბამბა",
                    source=invalid_source,
                )

                with self.assertRaises(ValidationError):
                    fact.full_clean()
                with self.assertRaises(ValidationError):
                    fact.save()

    def test_material_fact_requires_confirmed_state(self):
        fact = ProductMaterialFact(
            business=self.business,
            product=self.product,
            canonical_material="ბამბა",
            original_text="ბამბა",
            source=ProductMaterialFact.Source.DESCRIPTION,
            confirmation_state="candidate",
        )

        with self.assertRaises(ValidationError):
            fact.full_clean()
        with self.assertRaises(ValidationError):
            fact.save()

    def test_material_fact_requires_matching_product_business(self):
        fact = ProductMaterialFact(
            business=self.business,
            product=self.other_product,
            canonical_material="ატლასი",
            original_text="ატლასი",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )

        with self.assertRaises(ValidationError):
            fact.full_clean()
        with self.assertRaises(ValidationError):
            fact.save()

    def test_product_deletion_is_protected_when_material_fact_exists(self):
        ProductMaterialFact.objects.create(
            business=self.business,
            product=self.product,
            canonical_material="ბამბა",
            original_text="ბამბა",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )

        with self.assertRaises(ProtectedError):
            self.product.delete()

    def test_business_deletion_is_protected_when_material_fact_exists(self):
        ProductMaterialFact.objects.create(
            business=self.business,
            product=self.product,
            canonical_material="ბამბა",
            original_text="ბამბა",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )

        with self.assertRaises(ProtectedError):
            self.business.delete()

    def test_material_candidate_does_not_create_confirmed_fact(self):
        result = recognize_product_description(
            "ბამბა",
            terms=(
                RecognitionTerm(
                    destination=SemanticDestination.MATERIAL,
                    canonical_value="ბამბა",
                ),
            ),
        )

        self.assertEqual(len(result.candidates_for(SemanticDestination.MATERIAL)), 1)
        self.assertEqual(result.confirmed_facts, ())
        self.assertEqual(ProductMaterialFact.objects.count(), 0)

    def test_material_fact_string_uses_canonical_material(self):
        fact = ProductMaterialFact.objects.create(
            business=self.business,
            product=self.product,
            canonical_material="ბამბა",
            original_text="ბამბა",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )

        self.assertEqual(str(fact), "ბამბა")


class MaterialRecognitionTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="material-recognition-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="material-recognition-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="შარვალი",
            description="100% ბამბა",
        )
        self.second_product = Product.objects.create(
            business=self.business,
            name="ქურთუკი",
            description="Cotton lining",
        )
        self.other_product = Product.objects.create(
            business=self.other_business,
            name="კაბა",
            description="ატლასი",
        )

    def test_recognizes_material_from_business_confirmed_facts(self):
        self._create_material_fact(
            business=self.business,
            product=self.product,
            canonical_material="ბამბა",
            original_text="100% ბამბა",
        )
        self._create_material_fact(
            business=self.other_business,
            product=self.other_product,
            canonical_material="ატლასი",
        )
        material_fact_count = ProductMaterialFact.objects.count()

        result = recognize_materials_for_business(
            "100% ბამბა და ატლასი",
            self.business,
        )

        material_candidates = result.candidates_for(SemanticDestination.MATERIAL)
        self.assertEqual(len(material_candidates), 1)
        self.assertEqual(material_candidates[0].canonical_value, "ბამბა")
        self.assertEqual(material_candidates[0].observed_text, "ბამბა")
        self.assertTrue(material_candidates[0].requires_confirmation)
        self.assertFalse(material_candidates[0].is_confirmed)
        self.assertEqual(result.confirmed_facts, ())
        self.assertEqual(ProductMaterialFact.objects.count(), material_fact_count)

    def test_material_recognition_does_not_leak_another_business_facts(self):
        self._create_material_fact(
            business=self.other_business,
            product=self.other_product,
            canonical_material="ატლასი",
        )

        result = recognize_materials_for_business("ატლასი", self.business)

        self.assertEqual(result.candidates_for(SemanticDestination.MATERIAL), ())
        self.assertEqual(result.confirmed_facts, ())

    def test_material_recognition_without_business_returns_no_candidates(self):
        self._create_material_fact(
            business=self.business,
            product=self.product,
            canonical_material="ბამბა",
        )

        result = recognize_materials_for_business("ბამბა", None)

        self.assertEqual(result.observed_text, "ბამბა")
        self.assertEqual(result.candidates, ())
        self.assertEqual(result.confirmed_facts, ())

    def test_material_terms_deduplicate_canonical_materials_case_insensitively(self):
        self._create_material_fact(
            business=self.business,
            product=self.product,
            canonical_material="  Cotton  ",
        )
        self._create_material_fact(
            business=self.business,
            product=self.second_product,
            canonical_material="cotton",
        )

        terms = material_terms_for_business(self.business)

        self.assertEqual(len(terms), 1)
        self.assertEqual(terms[0].destination, SemanticDestination.MATERIAL)
        self.assertEqual(terms[0].canonical_value.casefold(), "cotton")

    def test_material_recognition_preserves_negation_boundary(self):
        self._create_material_fact(
            business=self.business,
            product=self.product,
            canonical_material="პოლიესტერი",
        )

        result = recognize_materials_for_business(
            "პოლიესტერი არ აქვს.",
            self.business,
        )

        self.assertEqual(result.candidates_for(SemanticDestination.MATERIAL), ())
        self.assertEqual(result.confirmed_facts, ())

    def _create_material_fact(
        self,
        business,
        product,
        canonical_material,
        original_text=None,
    ):
        return ProductMaterialFact.objects.create(
            business=business,
            product=product,
            canonical_material=canonical_material,
            original_text=original_text or canonical_material,
            source=ProductMaterialFact.Source.DESCRIPTION,
        )


class ProductTypeRecognitionTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="recognition-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="recognition-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )

    def test_recognizes_product_type_from_active_business_vocabulary(self):
        BusinessProductType.objects.create(
            business=self.business,
            name="შარვალი",
        )
        BusinessProductType.objects.create(
            business=self.other_business,
            name="კაბა",
        )

        result = recognize_product_types_for_business(
            "კლასიკური კაბა და შარვალი",
            self.business,
        )

        product_type_candidates = result.candidates_for(
            SemanticDestination.PRODUCT_TYPE
        )
        self.assertEqual(len(product_type_candidates), 1)
        self.assertEqual(product_type_candidates[0].canonical_value, "შარვალი")
        self.assertEqual(product_type_candidates[0].observed_text, "შარვალი")
        self.assertTrue(product_type_candidates[0].requires_confirmation)
        self.assertFalse(product_type_candidates[0].is_confirmed)
        self.assertEqual(result.confirmed_facts, ())

    def test_recognizes_product_type_alias_as_canonical_candidate(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="შარვალი",
        )
        BusinessProductTypeAlias.objects.create(
            business=self.business,
            product_type=product_type,
            alias="pants",
        )

        result = recognize_product_types_for_business(
            "classic pants",
            self.business,
        )

        product_type_candidates = result.candidates_for(
            SemanticDestination.PRODUCT_TYPE
        )
        self.assertEqual(len(product_type_candidates), 1)
        self.assertEqual(product_type_candidates[0].canonical_value, "შარვალი")
        self.assertEqual(product_type_candidates[0].observed_text, "pants")
        self.assertTrue(product_type_candidates[0].requires_confirmation)
        self.assertFalse(product_type_candidates[0].is_confirmed)
        self.assertEqual(result.confirmed_facts, ())

    def test_product_type_alias_recognition_does_not_leak_other_business_aliases(self):
        other_type = BusinessProductType.objects.create(
            business=self.other_business,
            name="კაბა",
        )
        BusinessProductTypeAlias.objects.create(
            business=self.other_business,
            product_type=other_type,
            alias="dress",
        )

        result = recognize_product_types_for_business("red dress", self.business)

        self.assertEqual(
            result.candidates_for(SemanticDestination.PRODUCT_TYPE),
            (),
        )
        self.assertEqual(result.confirmed_facts, ())

    def test_product_type_recognition_does_not_leak_another_business_vocabulary(self):
        BusinessProductType.objects.create(
            business=self.other_business,
            name="კაბა",
        )

        result = recognize_product_types_for_business("წითელი კაბა", self.business)

        self.assertEqual(
            result.candidates_for(SemanticDestination.PRODUCT_TYPE),
            (),
        )
        self.assertEqual(result.confirmed_facts, ())

    def test_product_type_recognition_without_business_returns_no_candidates(self):
        result = recognize_product_types_for_business("შარვალი", None)

        self.assertEqual(result.observed_text, "შარვალი")
        self.assertEqual(result.candidates, ())
        self.assertEqual(result.confirmed_facts, ())


class TagRecognitionTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="tag-recognition-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="tag-recognition-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )

    def test_recognizes_tag_from_active_business_vocabulary(self):
        BusinessTag.objects.create(
            business=self.business,
            name="ჯიბეები",
        )
        BusinessTag.objects.create(
            business=self.other_business,
            name="კლასიკური",
        )

        result = recognize_tags_for_business(
            "კლასიკური შარვალი ჯიბეები",
            self.business,
        )

        tag_candidates = result.candidates_for(SemanticDestination.TAG)
        self.assertEqual(len(tag_candidates), 1)
        self.assertEqual(tag_candidates[0].canonical_value, "ჯიბეები")
        self.assertEqual(tag_candidates[0].observed_text, "ჯიბეები")
        self.assertTrue(tag_candidates[0].requires_confirmation)
        self.assertFalse(tag_candidates[0].is_confirmed)
        self.assertEqual(result.confirmed_facts, ())

    def test_recognizes_tag_alias_as_canonical_candidate(self):
        tag = BusinessTag.objects.create(
            business=self.business,
            name="ჯიბეები",
        )
        BusinessTagAlias.objects.create(
            business=self.business,
            tag=tag,
            alias="pockets",
        )

        result = recognize_tags_for_business(
            "black trousers with pockets",
            self.business,
        )

        tag_candidates = result.candidates_for(SemanticDestination.TAG)
        self.assertEqual(len(tag_candidates), 1)
        self.assertEqual(tag_candidates[0].canonical_value, "ჯიბეები")
        self.assertEqual(tag_candidates[0].observed_text, "pockets")
        self.assertTrue(tag_candidates[0].requires_confirmation)
        self.assertFalse(tag_candidates[0].is_confirmed)
        self.assertEqual(result.confirmed_facts, ())

    def test_tag_alias_recognition_does_not_leak_other_business_aliases(self):
        other_tag = BusinessTag.objects.create(
            business=self.other_business,
            name="კლასიკური",
        )
        BusinessTagAlias.objects.create(
            business=self.other_business,
            tag=other_tag,
            alias="classic",
        )

        result = recognize_tags_for_business("classic trousers", self.business)

        self.assertEqual(
            result.candidates_for(SemanticDestination.TAG),
            (),
        )
        self.assertEqual(result.confirmed_facts, ())

    def test_tag_recognition_does_not_leak_another_business_vocabulary(self):
        BusinessTag.objects.create(
            business=self.other_business,
            name="კლასიკური",
        )

        result = recognize_tags_for_business("კლასიკური შარვალი", self.business)

        self.assertEqual(
            result.candidates_for(SemanticDestination.TAG),
            (),
        )
        self.assertEqual(result.confirmed_facts, ())

    def test_tag_recognition_without_business_returns_no_candidates(self):
        result = recognize_tags_for_business("ჯიბეები", None)

        self.assertEqual(result.observed_text, "ჯიბეები")
        self.assertEqual(result.candidates, ())
        self.assertEqual(result.confirmed_facts, ())


class ProductModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )

    def test_product_belongs_to_business(self):
        product = Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
        )

        self.assertEqual(product.business, self.business)
        self.assertEqual(self.business.products.get(), product)

    def test_product_requires_business(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Product.objects.create(
                    name="Ownerless product",
                    description="No business boundary.",
                )

    def test_product_requires_name_and_description(self):
        nameless = Product(business=self.business, name="", description="Description.")
        descriptionless = Product(
            business=self.business,
            name="Black trousers",
            description="",
        )

        with self.assertRaises(ValidationError):
            nameless.full_clean()
        with self.assertRaises(ValidationError):
            descriptionless.full_clean()

    def test_product_defaults_to_draft_lifecycle(self):
        product = Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
        )

        self.assertEqual(product.lifecycle, Product.Lifecycle.DRAFT)

    def test_product_accepts_active_lifecycle(self):
        product = Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )

        self.assertEqual(product.lifecycle, Product.Lifecycle.ACTIVE)

    def test_product_rejects_unknown_lifecycle_value(self):
        product = Product(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
            lifecycle="archived",
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_business_deletion_is_protected_when_product_exists(self):
        Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
        )

        with self.assertRaises(ProtectedError):
            self.business.delete()

    def test_product_query_can_be_scoped_by_business(self):
        owned_product = Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
        )
        Product.objects.create(
            business=self.other_business,
            name="Red dress",
            description="Red dress from another business.",
        )

        products = list(Product.objects.filter(business=self.business))

        self.assertEqual(products, [owned_product])

    def test_product_string_uses_name(self):
        product = Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
        )

        self.assertEqual(str(product), "Black trousers")


class ProductChoiceModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="choice-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="choice-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
        )
        self.second_product = Product.objects.create(
            business=self.business,
            name="Black blouse",
            description="Classic black blouse.",
        )
        self.other_product = Product.objects.create(
            business=self.other_business,
            name="Black dress",
            description="Black dress from another Business.",
        )

    def test_choice_belongs_to_business_and_product(self):
        choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size="M",
            color="Black",
            quantity=2,
        )

        self.assertEqual(choice.business, self.business)
        self.assertEqual(choice.product, self.product)
        self.assertEqual(choice.quantity, 2)
        self.assertTrue(choice.is_active)
        self.assertEqual(self.business.product_choices.get(), choice)
        self.assertEqual(self.product.choices.get(), choice)

    def test_choice_requires_business_and_product(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductChoice.objects.create(
                    product=self.product,
                    size="M",
                    color="Black",
                )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductChoice.objects.create(
                    business=self.business,
                    size="M",
                    color="Black",
                )

    def test_choice_requires_non_blank_size_and_color(self):
        for field_name in ("size", "color"):
            with self.subTest(field_name=field_name):
                choice = ProductChoice(
                    business=self.business,
                    product=self.product,
                    size="M",
                    color="Black",
                )
                setattr(choice, field_name, "   ")

                with self.assertRaises(ValidationError):
                    choice.full_clean()
                with self.assertRaises(ValidationError):
                    choice.save()

    def test_choice_strips_size_and_color_on_save(self):
        choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size="  M  ",
            color="  Black  ",
        )

        self.assertEqual(choice.size, "M")
        self.assertEqual(choice.color, "Black")

    def test_choice_quantity_accepts_zero_and_rejects_negative_values(self):
        choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size="M",
            color="Black",
            quantity=0,
        )

        self.assertEqual(choice.quantity, 0)

        invalid_choice = ProductChoice(
            business=self.business,
            product=self.product,
            size="L",
            color="Black",
            quantity=-1,
        )
        with self.assertRaises(ValidationError):
            invalid_choice.full_clean()
        with self.assertRaises(ValidationError):
            invalid_choice.save()

    def test_choice_active_state_is_explicit(self):
        choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size="M",
            color="Black",
            is_active=False,
        )

        self.assertFalse(choice.is_active)

    def test_choice_requires_matching_product_business(self):
        choice = ProductChoice(
            business=self.business,
            product=self.other_product,
            size="M",
            color="Black",
        )

        with self.assertRaises(ValidationError):
            choice.full_clean()
        with self.assertRaises(ValidationError):
            choice.save()

    def test_duplicate_choices_are_allowed_after_case_and_trim_normalization(self):
        first_choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size="M",
            color="Black",
            quantity=1,
            is_active=False,
        )
        second_choice = ProductChoice(
            business=self.business,
            product=self.product,
            size=" m ",
            color=" black ",
            quantity=3,
        )

        second_choice.full_clean()
        second_choice.save()

        self.assertNotEqual(first_choice.pk, second_choice.pk)
        self.assertEqual(ProductChoice.objects.filter(product=self.product).count(), 2)
        self.assertEqual(second_choice.size, "m")
        self.assertEqual(second_choice.color, "black")
        self.assertEqual(first_choice.quantity, 1)
        self.assertEqual(second_choice.quantity, 3)
        self.assertFalse(first_choice.is_active)
        self.assertTrue(second_choice.is_active)

    def test_same_size_color_combination_is_allowed_on_another_product(self):
        ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size="M",
            color="Black",
        )

        same_business_choice = ProductChoice.objects.create(
            business=self.business,
            product=self.second_product,
            size="m",
            color="black",
        )
        other_business_choice = ProductChoice.objects.create(
            business=self.other_business,
            product=self.other_product,
            size="M",
            color="Black",
        )

        self.assertEqual(ProductChoice.objects.count(), 3)
        self.assertEqual(same_business_choice.product, self.second_product)
        self.assertEqual(other_business_choice.business, self.other_business)

    def test_product_deletion_is_protected_when_choice_exists(self):
        ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size="M",
            color="Black",
        )

        with self.assertRaises(ProtectedError):
            self.product.delete()

    def test_business_deletion_is_protected_when_choice_exists(self):
        ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size="M",
            color="Black",
        )

        with self.assertRaises(ProtectedError):
            self.business.delete()

    def test_choice_suggestion_does_not_create_product_choice(self):
        result = recognize_choice_suggestions(
            "M size and Black color",
            size_values=("M",),
            color_values=("Black",),
        )

        self.assertEqual(len(result.candidates), 2)
        self.assertEqual(result.confirmed_facts, ())
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_choice_string_uses_product_size_and_color(self):
        choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size="M",
            color="Black",
        )

        self.assertEqual(str(choice), "Black trousers: M / Black")


class ProductFormTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="form-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="form-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )

    def test_form_exposes_only_approved_product_fields(self):
        form = ProductForm()

        self.assertEqual(list(form.fields), ["name", "description", "lifecycle"])

    def test_form_requires_name_and_description(self):
        form = ProductForm(
            data={
                "name": "",
                "description": "",
                "lifecycle": Product.Lifecycle.DRAFT,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("description", form.errors)

    def test_form_rejects_unknown_lifecycle(self):
        form = ProductForm(
            data={
                "name": "Black trousers",
                "description": "Classic black trousers.",
                "lifecycle": "archived",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("lifecycle", form.errors)

    def test_form_leaves_business_assignment_to_server_side_caller(self):
        form = ProductForm(
            data={
                "business": self.other_business.pk,
                "name": "Black trousers",
                "description": "Classic black trousers.",
                "lifecycle": Product.Lifecycle.ACTIVE,
            }
        )

        self.assertTrue(form.is_valid())

        product = form.save(commit=False)
        product.business = self.business
        product.save()

        self.assertEqual(product.business, self.business)
        self.assertEqual(product.name, "Black trousers")
        self.assertEqual(product.description, "Classic black trousers.")
        self.assertEqual(product.lifecycle, Product.Lifecycle.ACTIVE)
        self.assertEqual(Product.objects.count(), 1)


class ProductChoiceFormTests(TestCase):
    def test_form_exposes_only_choice_owned_fields(self):
        form = ProductChoiceForm()

        self.assertEqual(
            list(form.fields),
            ["size", "color", "quantity", "is_active"],
        )

    def test_form_ignores_submitted_business_and_product(self):
        form = ProductChoiceForm(
            data={
                "business": 999,
                "product": 999,
                "size": "M",
                "color": "Black",
                "quantity": 2,
                "is_active": True,
            }
        )

        self.assertTrue(form.is_valid())
        choice = form.save(commit=False)
        self.assertIsNone(choice.business_id)
        self.assertIsNone(choice.product_id)


class ProductChoiceFormSetTests(TestCase):
    prefix = "choices"

    def setUp(self):
        owner = get_user_model().objects.create_user(
            email="choice-formset-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(owner=owner, name="Seller Studio")

    def formset_data(self, rows, *, initial_forms=0):
        data = {
            f"{self.prefix}-TOTAL_FORMS": str(len(rows)),
            f"{self.prefix}-INITIAL_FORMS": str(initial_forms),
            f"{self.prefix}-MIN_NUM_FORMS": "0",
            f"{self.prefix}-MAX_NUM_FORMS": "1000",
        }
        for index, row in enumerate(rows):
            for field, value in row.items():
                data[f"{self.prefix}-{index}-{field}"] = value
        return data

    def build_formset(self, product, rows, *, initial_forms=0):
        return ProductChoiceFormSet(
            data=self.formset_data(rows, initial_forms=initial_forms),
            instance=product,
            prefix=self.prefix,
            queryset=ProductChoice.objects.filter(business=self.business),
        )

    def test_draft_product_allows_an_empty_extra_row(self):
        product = Product(
            business=self.business,
            name="Draft trousers",
            description="Draft description.",
            lifecycle=Product.Lifecycle.DRAFT,
        )

        formset = self.build_formset(product, [{}])

        self.assertTrue(formset.is_valid())

    def test_active_product_requires_at_least_one_active_choice(self):
        product = Product(
            business=self.business,
            name="Active trousers",
            description="Active description.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )

        formset = self.build_formset(product, [])

        self.assertFalse(formset.is_valid())
        self.assertIn(
            "An active product requires at least one active choice.",
            formset.non_form_errors(),
        )

    def test_partially_completed_choice_keeps_field_errors(self):
        product = Product(
            business=self.business,
            name="Draft trousers",
            description="Draft description.",
            lifecycle=Product.Lifecycle.DRAFT,
        )
        rows = [
            {
                "size": "M",
                "color": "",
                "quantity": "2",
                "is_active": "on",
            }
        ]

        formset = self.build_formset(product, rows)

        self.assertFalse(formset.is_valid())
        self.assertIn("color", formset.forms[0].errors)
        self.assertEqual(formset.forms[0].data[f"{self.prefix}-0-size"], "M")

    def test_normalized_duplicate_choice_rows_are_valid(self):
        product = Product(
            business=self.business,
            name="Active trousers",
            description="Active description.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        rows = [
            {
                "size": "M",
                "color": "Black",
                "quantity": "1",
                "is_active": "on",
            },
            {
                "size": " m ",
                "color": " black ",
                "quantity": "3",
                "is_active": "on",
            },
        ]

        formset = self.build_formset(product, rows)

        self.assertTrue(formset.is_valid())

    def test_deleting_last_active_choice_is_invalid_for_active_product(self):
        product = Product.objects.create(
            business=self.business,
            name="Active trousers",
            description="Active description.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size="M",
            color="Black",
            quantity=1,
        )
        rows = [
            {
                "id": str(choice.pk),
                "size": choice.size,
                "color": choice.color,
                "quantity": str(choice.quantity),
                "is_active": "on",
                "DELETE": "on",
            }
        ]

        formset = self.build_formset(product, rows, initial_forms=1)

        self.assertFalse(formset.is_valid())
        self.assertIn(
            "An active product requires at least one active choice.",
            formset.non_form_errors(),
        )


class ProductBundleTests(TestCase):
    prefix = "choices"

    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="bundle-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="bundle-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )

    def bundle_data(
        self,
        rows,
        *,
        lifecycle=Product.Lifecycle.ACTIVE,
        initial_forms=0,
        name="Black trousers",
    ):
        data = {
            "name": name,
            "description": "Classic black trousers.",
            "lifecycle": lifecycle,
            f"{self.prefix}-TOTAL_FORMS": str(len(rows)),
            f"{self.prefix}-INITIAL_FORMS": str(initial_forms),
            f"{self.prefix}-MIN_NUM_FORMS": "0",
            f"{self.prefix}-MAX_NUM_FORMS": "1000",
        }
        for index, row in enumerate(rows):
            for field, value in row.items():
                data[f"{self.prefix}-{index}-{field}"] = value
        return data

    def active_choice_row(self, **overrides):
        row = {
            "size": "M",
            "color": "Black",
            "quantity": "2",
            "is_active": "on",
        }
        row.update(overrides)
        return row

    def test_valid_create_assigns_ownership_and_saves_one_bundle(self):
        bundle = ProductBundle(
            business=self.business,
            data=self.bundle_data([self.active_choice_row()]),
        )

        self.assertTrue(bundle.is_valid())
        product = bundle.save()

        self.assertEqual(product.business, self.business)
        self.assertEqual(product.lifecycle, Product.Lifecycle.ACTIVE)
        choice = ProductChoice.objects.get()
        self.assertEqual(choice.business, self.business)
        self.assertEqual(choice.product, product)
        self.assertEqual(choice.size, "M")
        self.assertEqual(choice.color, "Black")
        self.assertEqual(choice.quantity, 2)

    def test_draft_product_can_save_without_choices(self):
        bundle = ProductBundle(
            business=self.business,
            data=self.bundle_data([{}], lifecycle=Product.Lifecycle.DRAFT),
        )

        self.assertTrue(bundle.is_valid())
        product = bundle.save()

        self.assertEqual(product.lifecycle, Product.Lifecycle.DRAFT)
        self.assertFalse(product.choices.exists())

    def test_invalid_choice_does_not_partially_persist_product(self):
        invalid_row = self.active_choice_row(color="")
        bundle = ProductBundle(
            business=self.business,
            data=self.bundle_data([invalid_row]),
        )

        self.assertFalse(bundle.is_valid())
        with self.assertRaisesMessage(
            ValueError,
            "Cannot save an invalid Product bundle.",
        ):
            bundle.save()

        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_choice_save_failure_rolls_back_product_and_choices(self):
        bundle = ProductBundle(
            business=self.business,
            data=self.bundle_data([self.active_choice_row()]),
        )
        self.assertTrue(bundle.is_valid())

        with patch(
            "catalog.product_bundles.ProductChoice.save",
            side_effect=IntegrityError("simulated choice write failure"),
        ):
            with self.assertRaisesMessage(
                IntegrityError,
                "simulated choice write failure",
            ):
                bundle.save()

        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_normalized_duplicate_rows_persist_as_distinct_choices(self):
        rows = [
            self.active_choice_row(quantity="1"),
            self.active_choice_row(size=" m ", color=" black ", quantity="3"),
        ]
        bundle = ProductBundle(
            business=self.business,
            data=self.bundle_data(rows),
        )

        self.assertTrue(bundle.is_valid())
        product = bundle.save()

        choices = list(product.choices.order_by("id"))
        self.assertEqual(len(choices), 2)
        self.assertNotEqual(choices[0].pk, choices[1].pk)
        self.assertEqual([choice.quantity for choice in choices], [1, 3])

    def test_existing_product_from_another_business_is_rejected(self):
        other_product = Product.objects.create(
            business=self.other_business,
            name="Other dress",
            description="Other description.",
            lifecycle=Product.Lifecycle.DRAFT,
        )
        bundle = ProductBundle(
            business=self.business,
            instance=other_product,
            data=self.bundle_data([{}], lifecycle=Product.Lifecycle.DRAFT),
        )

        self.assertFalse(bundle.is_valid())
        self.assertIn(
            "Product must belong to the active Business.",
            bundle.product_form.non_field_errors(),
        )
        with self.assertRaisesMessage(
            ValueError,
            "Cannot save an invalid Product bundle.",
        ):
            bundle.save()

        other_product.refresh_from_db()
        self.assertEqual(other_product.name, "Other dress")

    def test_forged_choice_id_cannot_mutate_another_business_choice(self):
        product = Product.objects.create(
            business=self.business,
            name="Owned trousers",
            description="Owned description.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        owned_choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size="M",
            color="Black",
            quantity=2,
        )
        other_product = Product.objects.create(
            business=self.other_business,
            name="Other dress",
            description="Other description.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        other_choice = ProductChoice.objects.create(
            business=self.other_business,
            product=other_product,
            size="L",
            color="Red",
            quantity=4,
        )
        forged_row = self.active_choice_row(
            id=str(other_choice.pk),
            quantity="99",
        )
        bundle = ProductBundle(
            business=self.business,
            instance=product,
            data=self.bundle_data([forged_row], initial_forms=1),
        )

        self.assertFalse(bundle.is_valid())
        self.assertIn("id", bundle.choice_formset.forms[0].errors)

        owned_choice.refresh_from_db()
        other_choice.refresh_from_db()
        self.assertEqual(owned_choice.quantity, 2)
        self.assertEqual(other_choice.quantity, 4)

    def test_valid_update_saves_product_and_choice_changes(self):
        product = Product.objects.create(
            business=self.business,
            name="Old trousers",
            description="Old description.",
            lifecycle=Product.Lifecycle.DRAFT,
        )
        choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size="M",
            color="Black",
            quantity=1,
        )
        row = self.active_choice_row(
            id=str(choice.pk),
            size="L",
            quantity="5",
        )
        bundle = ProductBundle(
            business=self.business,
            instance=product,
            data=self.bundle_data(
                [row],
                lifecycle=Product.Lifecycle.ACTIVE,
                initial_forms=1,
                name="Updated trousers",
            ),
        )

        self.assertTrue(bundle.is_valid())
        bundle.save()

        product.refresh_from_db()
        choice.refresh_from_db()
        self.assertEqual(product.name, "Updated trousers")
        self.assertEqual(product.lifecycle, Product.Lifecycle.ACTIVE)
        self.assertEqual(choice.size, "L")
        self.assertEqual(choice.quantity, 5)

    def test_active_product_cannot_delete_its_last_active_choice(self):
        product = Product.objects.create(
            business=self.business,
            name="Active trousers",
            description="Active description.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size="M",
            color="Black",
            quantity=1,
        )
        row = self.active_choice_row(
            id=str(choice.pk),
            quantity="1",
            DELETE="on",
        )
        bundle = ProductBundle(
            business=self.business,
            instance=product,
            data=self.bundle_data([row], initial_forms=1, name="Changed name"),
        )

        self.assertFalse(bundle.is_valid())
        with self.assertRaisesMessage(
            ValueError,
            "Cannot save an invalid Product bundle.",
        ):
            bundle.save()

        product.refresh_from_db()
        self.assertEqual(product.name, "Active trousers")
        self.assertTrue(ProductChoice.objects.filter(pk=choice.pk).exists())

    def test_draft_product_can_delete_all_choices(self):
        product = Product.objects.create(
            business=self.business,
            name="Draft trousers",
            description="Draft description.",
            lifecycle=Product.Lifecycle.DRAFT,
        )
        choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size="M",
            color="Black",
            quantity=1,
        )
        row = self.active_choice_row(
            id=str(choice.pk),
            quantity="1",
            DELETE="on",
        )
        bundle = ProductBundle(
            business=self.business,
            instance=product,
            data=self.bundle_data(
                [row],
                lifecycle=Product.Lifecycle.DRAFT,
                initial_forms=1,
            ),
        )

        self.assertTrue(bundle.is_valid())
        bundle.save()

        self.assertFalse(ProductChoice.objects.filter(pk=choice.pk).exists())


class ProductListViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="list-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="list-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )
        self.url = reverse("catalog:product_list")

    def test_product_list_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_product_list_renders_only_active_business_products(self):
        owned_product = Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        Product.objects.create(
            business=self.other_business,
            name="Red dress",
            description="Red dress from another business.",
        )
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_list.html")
        self.assertContains(response, "Products")
        self.assertContains(response, owned_product.name)
        self.assertContains(response, owned_product.description)
        self.assertContains(response, "Active")
        self.assertContains(response, "Add product")
        self.assertContains(response, "Edit")
        self.assertContains(response, 'aria-current="page"')
        self.assertNotContains(response, "Red dress")
        self.assertEqual(list(response.context["products"]), [owned_product])

    def test_product_list_without_business_shows_empty_state_without_creating_business(
        self,
    ):
        seller_without_business = get_user_model().objects.create_user(
            email="no-business@example.com",
            password="test-password",
        )
        Product.objects.create(
            business=self.other_business,
            name="Other product",
            description="Other owner's product.",
        )
        self.client.force_login(seller_without_business)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No business workspace yet.")
        self.assertNotContains(response, "Other product")
        self.assertFalse(
            Business.objects.filter(owner=seller_without_business).exists()
        )

    def test_product_list_with_business_but_no_products_shows_empty_state(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products yet.")

    def test_product_list_refuses_multiple_businesses_without_switcher(self):
        second_business = Business.objects.create(
            owner=self.owner,
            name="Second Studio",
        )
        Product.objects.create(
            business=self.business,
            name="First business product",
            description="Should not be selected implicitly.",
        )
        Product.objects.create(
            business=second_business,
            name="Second business product",
            description="Should not be selected implicitly.",
        )
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 409)
        self.assertContains(
            response,
            "Multiple business workspaces need an approved switcher",
            status_code=409,
        )
        self.assertNotContains(response, "First business product", status_code=409)
        self.assertNotContains(response, "Second business product", status_code=409)


class ProductCreateViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="create-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="create-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )
        self.url = reverse("catalog:product_create")
        self.list_url = reverse("catalog:product_list")

    def test_product_create_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_product_create_renders_approved_form_fields(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_form.html")
        self.assertContains(response, "Add product")
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, 'name="lifecycle"')
        self.assertContains(response, "Create product")
        self.assertNotContains(response, 'name="business"')

    def test_product_create_without_business_shows_workspace_state(self):
        seller_without_business = get_user_model().objects.create_user(
            email="create-no-business@example.com",
            password="test-password",
        )
        self.client.force_login(seller_without_business)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No business workspace yet.")
        self.assertNotContains(response, 'name="name"')

    def test_product_create_post_without_business_does_not_create_product(self):
        seller_without_business = get_user_model().objects.create_user(
            email="create-post-no-business@example.com",
            password="test-password",
        )
        self.client.force_login(seller_without_business)

        response = self.client.post(
            self.url,
            {
                "name": "Black trousers",
                "description": "Classic black trousers.",
                "lifecycle": Product.Lifecycle.ACTIVE,
            },
        )

        self.assertEqual(response.status_code, 409)
        self.assertContains(
            response,
            "No business workspace yet.",
            status_code=409,
        )
        self.assertEqual(Product.objects.count(), 0)

    def test_product_create_refuses_multiple_businesses_without_switcher(self):
        Business.objects.create(owner=self.owner, name="Second Studio")
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 409)
        self.assertContains(
            response,
            "Multiple business workspaces need an approved switcher",
            status_code=409,
        )
        self.assertNotContains(response, 'name="name"', status_code=409)

    def test_product_create_assigns_business_server_side(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {
                "business": self.other_business.pk,
                "name": "Black trousers",
                "description": "Classic black trousers.",
                "lifecycle": Product.Lifecycle.ACTIVE,
            },
        )

        self.assertRedirects(response, self.list_url)
        product = Product.objects.get()
        self.assertEqual(product.business, self.business)
        self.assertEqual(product.name, "Black trousers")
        self.assertEqual(product.description, "Classic black trousers.")
        self.assertEqual(product.lifecycle, Product.Lifecycle.ACTIVE)

    def test_product_create_preserves_validation_errors_without_creating_product(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {
                "name": "",
                "description": "",
                "lifecycle": Product.Lifecycle.ACTIVE,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_form.html")
        self.assertContains(response, "This field is required.")
        self.assertEqual(Product.objects.count(), 0)

    def test_product_create_rejects_external_next_url(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            f"{self.url}?next=https://example.com/escape",
            {
                "name": "Black trousers",
                "description": "Classic black trousers.",
                "lifecycle": Product.Lifecycle.ACTIVE,
            },
        )

        self.assertRedirects(response, self.list_url)
        self.assertNotIn("example.com", response["Location"])


class ProductUpdateViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="edit-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="edit-other-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
            lifecycle=Product.Lifecycle.DRAFT,
        )
        self.other_product = Product.objects.create(
            business=self.other_business,
            name="Red dress",
            description="Red dress from another business.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        self.url = reverse("catalog:product_edit", kwargs={"pk": self.product.pk})
        self.list_url = reverse("catalog:product_list")

    def test_product_edit_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_product_edit_renders_form_for_owned_product(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_form.html")
        self.assertContains(response, "Edit Black trousers")
        self.assertContains(response, 'value="Black trousers"')
        self.assertContains(response, "Classic black trousers.")
        self.assertContains(response, "Save changes")
        self.assertNotContains(response, 'name="business"')

    def test_product_edit_updates_owned_product(self):
        self.client.force_login(self.owner)
        return_url = f"{self.list_url}?from=edit"

        response = self.client.post(
            self.url,
            {
                "next": return_url,
                "name": "Updated trousers",
                "description": "Updated description.",
                "lifecycle": Product.Lifecycle.ACTIVE,
            },
        )

        self.assertRedirects(response, return_url)
        self.product.refresh_from_db()
        self.assertEqual(self.product.business, self.business)
        self.assertEqual(self.product.name, "Updated trousers")
        self.assertEqual(self.product.description, "Updated description.")
        self.assertEqual(self.product.lifecycle, Product.Lifecycle.ACTIVE)

    def test_product_edit_preserves_validation_errors_without_changing_product(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {
                "name": "",
                "description": "",
                "lifecycle": "archived",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_form.html")
        self.assertContains(response, "This field is required.")
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Black trousers")
        self.assertEqual(self.product.description, "Classic black trousers.")
        self.assertEqual(self.product.lifecycle, Product.Lifecycle.DRAFT)

    def test_product_edit_hides_another_business_product(self):
        self.client.force_login(self.owner)
        other_url = reverse(
            "catalog:product_edit",
            kwargs={"pk": self.other_product.pk},
        )

        response = self.client.get(other_url)

        self.assertEqual(response.status_code, 404)

    def test_product_edit_post_hides_another_business_product_without_change(self):
        self.client.force_login(self.owner)
        other_url = reverse(
            "catalog:product_edit",
            kwargs={"pk": self.other_product.pk},
        )

        response = self.client.post(
            other_url,
            {
                "name": "Leaked update",
                "description": "Should not save.",
                "lifecycle": Product.Lifecycle.DRAFT,
            },
        )

        self.assertEqual(response.status_code, 404)
        self.other_product.refresh_from_db()
        self.assertEqual(self.other_product.name, "Red dress")
        self.assertEqual(self.other_product.lifecycle, Product.Lifecycle.ACTIVE)

    def test_product_edit_refuses_multiple_businesses_without_switcher(self):
        Business.objects.create(owner=self.owner, name="Second Studio")
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 409)
        self.assertContains(
            response,
            "Multiple business workspaces need an approved switcher",
            status_code=409,
        )
        self.assertNotContains(response, "Black trousers", status_code=409)
