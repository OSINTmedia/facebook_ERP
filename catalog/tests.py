from dataclasses import FrozenInstanceError
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import quote

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from businesses.models import Business
from catalog.forms import (
    ChoiceVocabularyEditForm,
    ChoiceVocabularyForm,
    ProductChoiceForm,
    ProductChoiceFormSet,
    ProductForm,
    ProductMaterialFactForm,
    ProductMaterialFactFormSet,
)
from catalog.material_transfers import transfer_material_candidate
from catalog.models import (
    BusinessColor,
    BusinessColorAlias,
    BusinessProductType,
    BusinessProductTypeAlias,
    BusinessSize,
    BusinessSizeAlias,
    BusinessTag,
    BusinessTagAlias,
    Product,
    ProductChoice,
    ProductMaterialFact,
    ProductTag,
)
from catalog.product_bundles import ProductBundle
from catalog.recognition import (
    RecognitionTerm,
    SemanticDestination,
    choice_suggestion_terms,
    choice_vocabulary_terms_for_business,
    material_terms_for_business,
    recognize_choice_suggestions,
    recognize_materials_for_business,
    recognize_product_preview_for_business,
    recognize_tags_for_business,
    recognize_product_types_for_business,
    recognize_product_description,
)
from catalog.vocabulary import (
    COLOR_VOCABULARY,
    PRODUCT_TYPE_VOCABULARY,
    SIZE_VOCABULARY,
    TAG_VOCABULARY,
    create_choice_vocabulary_entry,
    update_choice_vocabulary_entry,
)


def size_value(business, name="M", *, is_active=True):
    size, _ = BusinessSize.objects.get_or_create(
        business=business,
        name=name,
        defaults={"is_active": is_active},
    )
    return size


def color_value(business, name="Black", *, is_active=True):
    color, _ = BusinessColor.objects.get_or_create(
        business=business,
        name=name,
        defaults={"is_active": is_active},
    )
    return color


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


class ProductRecognitionPreviewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="preview-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="preview-other-owner@example.com",
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

    def seed_vocabulary(
        self,
        business,
        *,
        product_type_name,
        product_type_alias,
        tag_name,
        material,
        size,
        color,
    ):
        product_type = BusinessProductType.objects.create(
            business=business,
            name=product_type_name,
        )
        BusinessProductTypeAlias.objects.create(
            business=business,
            product_type=product_type,
            alias=product_type_alias,
        )
        BusinessTag.objects.create(
            business=business,
            name=tag_name,
        )
        source_product = Product.objects.create(
            business=business,
            name=f"{product_type_name} vocabulary source",
            description="Stored vocabulary source.",
        )
        ProductMaterialFact.objects.create(
            business=business,
            product=source_product,
            canonical_material=material,
            original_text=material,
            source=ProductMaterialFact.Source.DESCRIPTION,
        )
        canonical_size = size_value(business, size)
        canonical_color = color_value(business, color)
        ProductChoice.objects.create(
            business=business,
            product=source_product,
            size=canonical_size,
            color=canonical_color,
        )
        return source_product

    def test_preview_composes_all_business_scoped_candidate_destinations(self):
        self.seed_vocabulary(
            self.business,
            product_type_name="Trousers",
            product_type_alias="pants",
            tag_name="Classic",
            material="Cotton",
            size="M",
            color="Black",
        )
        counts_before = (
            Product.objects.count(),
            ProductChoice.objects.count(),
            ProductMaterialFact.objects.count(),
        )

        result = recognize_product_preview_for_business(
            "pants Classic Cotton M Black",
            self.business,
        )

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
                (SemanticDestination.PRODUCT_TYPE, "Trousers", "pants"),
                (SemanticDestination.TAG, "Classic", "Classic"),
                (SemanticDestination.MATERIAL, "Cotton", "Cotton"),
                (SemanticDestination.CHOICE_SIZE, "M", "M"),
                (SemanticDestination.CHOICE_COLOR, "Black", "Black"),
            ],
        )
        self.assertTrue(
            all(candidate.requires_confirmation for candidate in result.candidates)
        )
        self.assertEqual(result.confirmed_facts, ())
        self.assertEqual(
            (
                Product.objects.count(),
                ProductChoice.objects.count(),
                ProductMaterialFact.objects.count(),
            ),
            counts_before,
        )

    def test_preview_excludes_other_business_and_negated_candidates(self):
        self.seed_vocabulary(
            self.business,
            product_type_name="Trousers",
            product_type_alias="pants",
            tag_name="Classic",
            material="Cotton",
            size="M",
            color="Black",
        )
        self.seed_vocabulary(
            self.other_business,
            product_type_name="Dress",
            product_type_alias="gown",
            tag_name="Private",
            material="Silk",
            size="L",
            color="Red",
        )

        result = recognize_product_preview_for_business(
            "Dress Private Silk L Red, no Cotton, without Black.",
            self.business,
        )

        self.assertEqual(result.candidates, ())
        self.assertEqual(result.confirmed_facts, ())

    def test_preview_resolves_explicit_size_and_color_aliases(self):
        self.seed_vocabulary(
            self.business,
            product_type_name="Trousers",
            product_type_alias="pants",
            tag_name="Classic",
            material="Cotton",
            size="M",
            color="Black",
        )
        canonical_size = BusinessSize.objects.get(
            business=self.business,
            name="M",
        )
        canonical_color = BusinessColor.objects.get(
            business=self.business,
            name="Black",
        )
        BusinessSizeAlias.objects.create(
            business=self.business,
            size=canonical_size,
            alias="M-ზომა",
        )
        BusinessColorAlias.objects.create(
            business=self.business,
            color=canonical_color,
            alias="შავი",
        )

        result = recognize_product_preview_for_business("M-ზომა, შავი", self.business)

        size_candidate = result.candidates_for(SemanticDestination.CHOICE_SIZE)[0]
        color_candidate = result.candidates_for(SemanticDestination.CHOICE_COLOR)[0]
        self.assertEqual(size_candidate.canonical_value, "M")
        self.assertEqual(size_candidate.observed_text, "M-ზომა")
        self.assertEqual(color_candidate.canonical_value, "Black")
        self.assertEqual(color_candidate.observed_text, "შავი")

    def test_preview_without_business_has_no_candidates(self):
        result = recognize_product_preview_for_business("pants M Black", None)

        self.assertEqual(result.observed_text, "pants M Black")
        self.assertEqual(result.candidates, ())
        self.assertEqual(result.confirmed_facts, ())


class ChoiceVocabularyFormTests(SimpleTestCase):
    def test_form_normalizes_and_deduplicates_explicit_aliases(self):
        form = ChoiceVocabularyForm(
            {
                "size-vocabulary-name": " M ",
                "size-vocabulary-aliases": "M-ზომა, M size\nM-ზომა",
            },
            kind=SIZE_VOCABULARY,
            prefix="size-vocabulary",
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "M")
        self.assertEqual(form.cleaned_data["aliases"], ("M-ზომა", "M size"))

    def test_form_rejects_alias_equal_to_canonical_value(self):
        form = ChoiceVocabularyForm(
            {
                "color-vocabulary-name": "შავი",
                "color-vocabulary-aliases": "Black, შავი",
            },
            kind=COLOR_VOCABULARY,
            prefix="color-vocabulary",
        )

        self.assertFalse(form.is_valid())
        self.assertIn("aliases", form.errors)

    def test_edit_form_prepares_current_name_aliases_and_active_state(self):
        size = SimpleNamespace(
            name="M",
            is_active=False,
            aliases=SimpleNamespace(
                all=lambda: (
                    SimpleNamespace(alias="M size"),
                    SimpleNamespace(alias="M-ზომა"),
                )
            ),
        )

        form = ChoiceVocabularyEditForm(
            kind=SIZE_VOCABULARY,
            instance=size,
            prefix="edit-size",
        )

        self.assertEqual(form["name"].value(), "M")
        self.assertEqual(form["aliases"].value(), "M size, M-ზომა")
        self.assertFalse(form["is_active"].value())

    def test_form_supports_product_type_and_tag_vocabulary(self):
        product_type_form = ChoiceVocabularyForm(
            {
                "type-name": " Shirt ",
                "type-aliases": "party shirt, პერანგი",
            },
            kind=PRODUCT_TYPE_VOCABULARY,
            prefix="type",
        )
        tag_form = ChoiceVocabularyForm(
            {
                "tag-name": " Party ",
                "tag-aliases": "partywear, საღამოს",
            },
            kind=TAG_VOCABULARY,
            prefix="tag",
        )

        self.assertTrue(product_type_form.is_valid())
        self.assertTrue(tag_form.is_valid())
        self.assertEqual(product_type_form.cleaned_data["name"], "Shirt")
        self.assertEqual(tag_form.cleaned_data["name"], "Party")


class ChoiceVocabularyModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        owner = user_model.objects.create_user(
            email="choice-vocabulary-owner@example.com",
            password="test-password",
        )
        other_owner = user_model.objects.create_user(
            email="choice-vocabulary-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(owner=owner, name="Seller Studio")
        self.other_business = Business.objects.create(
            owner=other_owner,
            name="Other Studio",
        )

    def test_canonical_values_are_normalized_unique_and_business_scoped(self):
        size = BusinessSize.objects.create(business=self.business, name="  M  ")
        color = BusinessColor.objects.create(business=self.business, name="  შავი  ")

        self.assertEqual(size.name, "M")
        self.assertEqual(color.name, "შავი")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BusinessSize.objects.create(business=self.business, name="m")

        other_size = BusinessSize.objects.create(
            business=self.other_business,
            name="m",
        )
        self.assertEqual(other_size.business, self.other_business)

    def test_aliases_require_the_same_business_and_cannot_collide_with_names(self):
        size = size_value(self.business)
        other_size = size_value(self.other_business, "L")
        BusinessSizeAlias.objects.create(
            business=self.business,
            size=size,
            alias="M-ზომა",
        )

        conflicting_alias = BusinessSizeAlias(
            business=self.business,
            size=size,
            alias="M",
        )
        with self.assertRaises(ValidationError):
            conflicting_alias.full_clean()
        with self.assertRaises(ValidationError):
            conflicting_alias.save()

        cross_business_alias = BusinessSizeAlias(
            business=self.business,
            size=other_size,
            alias="Large",
        )
        with self.assertRaises(ValidationError):
            cross_business_alias.full_clean()
        with self.assertRaises(ValidationError):
            cross_business_alias.save()

    def test_contextual_creation_is_atomic_when_an_alias_conflicts(self):
        existing_size = size_value(self.business, "S")
        BusinessSizeAlias.objects.create(
            business=self.business,
            size=existing_size,
            alias="small",
        )

        with self.assertRaises(ValidationError):
            create_choice_vocabulary_entry(
                business=self.business,
                kind=SIZE_VOCABULARY,
                name="M",
                aliases=("M-ზომა", "small"),
            )

        self.assertFalse(BusinessSize.objects.filter(business=self.business, name="M").exists())
        self.assertFalse(
            BusinessSizeAlias.objects.filter(
                business=self.business,
                alias="M-ზომა",
            ).exists()
        )

    def test_recognition_uses_only_active_vocabulary_from_the_supplied_business(self):
        owned_size = size_value(self.business, "M")
        inactive_color = color_value(self.business, "შავი")
        inactive_color.is_active = False
        inactive_color.save(update_fields=["is_active"])
        other_color = color_value(self.other_business, "Red")
        BusinessSizeAlias.objects.create(
            business=self.business,
            size=owned_size,
            alias="M-ზომა",
        )
        BusinessColorAlias.objects.create(
            business=self.other_business,
            color=other_color,
            alias="წითელი",
        )

        terms = choice_vocabulary_terms_for_business(self.business)
        result = recognize_product_description("M-ზომა, შავი, წითელი", terms=terms)

        self.assertEqual(
            [
                (candidate.destination, candidate.canonical_value)
                for candidate in result.candidates
            ],
            [(SemanticDestination.CHOICE_SIZE, "M")],
        )

    def test_update_replaces_aliases_and_preserves_referenced_choice(self):
        size = size_value(self.business, "M")
        color = color_value(self.business, "Black")
        old_alias = BusinessSizeAlias.objects.create(
            business=self.business,
            size=size,
            alias="M size",
        )
        product = Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
        )
        choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=size,
            color=color,
            quantity=7,
        )

        updated_size = update_choice_vocabulary_entry(
            business=self.business,
            kind=SIZE_VOCABULARY,
            entry_id=size.pk,
            name="Medium",
            aliases=("M", "M-ზომა"),
            is_active=False,
        )

        choice.refresh_from_db()
        self.assertEqual(updated_size.pk, size.pk)
        self.assertEqual(updated_size.name, "Medium")
        self.assertFalse(updated_size.is_active)
        self.assertEqual(choice.size_id, size.pk)
        self.assertEqual(choice.quantity, 7)
        self.assertFalse(BusinessSizeAlias.objects.filter(pk=old_alias.pk).exists())
        self.assertEqual(
            set(updated_size.aliases.values_list("alias", flat=True)),
            {"M", "M-ზომა"},
        )

    def test_update_rolls_back_when_replacement_alias_conflicts(self):
        medium = size_value(self.business, "M")
        small = size_value(self.business, "S")
        BusinessSizeAlias.objects.create(
            business=self.business,
            size=medium,
            alias="M size",
        )
        BusinessSizeAlias.objects.create(
            business=self.business,
            size=small,
            alias="Small",
        )

        with self.assertRaises(ValidationError):
            update_choice_vocabulary_entry(
                business=self.business,
                kind=SIZE_VOCABULARY,
                entry_id=medium.pk,
                name="Medium",
                aliases=("M-ზომა", "Small"),
                is_active=False,
            )

        medium.refresh_from_db()
        self.assertEqual(medium.name, "M")
        self.assertTrue(medium.is_active)
        self.assertEqual(
            list(medium.aliases.values_list("alias", flat=True)),
            ["M size"],
        )
        self.assertFalse(
            BusinessSizeAlias.objects.filter(
                business=self.business,
                alias="M-ზომა",
            ).exists()
        )

    def test_update_rejects_entry_from_another_business(self):
        other_color = color_value(self.other_business, "Red")

        with self.assertRaises(ValidationError):
            update_choice_vocabulary_entry(
                business=self.business,
                kind=COLOR_VOCABULARY,
                entry_id=other_color.pk,
                name="Blue",
                aliases=("ლურჯი",),
            )

        other_color.refresh_from_db()
        self.assertEqual(other_color.name, "Red")
        self.assertFalse(other_color.aliases.exists())

    def test_product_type_update_preserves_product_reference(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Shirt",
        )
        product = Product.objects.create(
            business=self.business,
            product_type=product_type,
            name="Party shirt",
            description="Party shirt.",
        )

        updated_type = update_choice_vocabulary_entry(
            business=self.business,
            kind=PRODUCT_TYPE_VOCABULARY,
            entry_id=product_type.pk,
            name="პერანგი",
            aliases=("Shirt", "party shirt"),
            is_active=False,
        )

        product.refresh_from_db()
        self.assertEqual(updated_type.pk, product_type.pk)
        self.assertFalse(updated_type.is_active)
        self.assertEqual(product.product_type_id, product_type.pk)
        self.assertEqual(
            set(updated_type.aliases.values_list("alias", flat=True)),
            {"Shirt", "party shirt"},
        )

    def test_tag_alias_replacement_rolls_back_on_collision(self):
        party = BusinessTag.objects.create(business=self.business, name="Party")
        classic = BusinessTag.objects.create(
            business=self.business,
            name="Classic",
        )
        BusinessTagAlias.objects.create(
            business=self.business,
            tag=party,
            alias="partywear",
        )
        BusinessTagAlias.objects.create(
            business=self.business,
            tag=classic,
            alias="formal",
        )

        with self.assertRaises(ValidationError):
            update_choice_vocabulary_entry(
                business=self.business,
                kind=TAG_VOCABULARY,
                entry_id=party.pk,
                name="Occasion",
                aliases=("evening", "formal"),
                is_active=False,
            )

        party.refresh_from_db()
        self.assertEqual(party.name, "Party")
        self.assertTrue(party.is_active)
        self.assertEqual(
            list(party.aliases.values_list("alias", flat=True)),
            ["partywear"],
        )

    def test_create_taxonomy_entry_rejects_another_canonical_alias(self):
        shirt = BusinessProductType.objects.create(
            business=self.business,
            name="Shirt",
        )
        BusinessProductTypeAlias.objects.create(
            business=self.business,
            product_type=shirt,
            alias="party shirt",
        )

        with self.assertRaises(ValidationError):
            create_choice_vocabulary_entry(
                business=self.business,
                kind=PRODUCT_TYPE_VOCABULARY,
                name="Top",
                aliases=("party shirt",),
            )

        self.assertFalse(
            BusinessProductType.objects.filter(
                business=self.business,
                name="Top",
            ).exists()
        )


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
        self.assertTrue(product_type.is_active)

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
        self.assertTrue(tag.is_active)

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


class ProductMaterialFactFormTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="material-form-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="material-form-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(owner=self.owner, name="Studio")
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="Trousers",
            description="Cotton trousers.",
        )

    def test_form_exposes_only_editable_material_fact_fields(self):
        form = ProductMaterialFactForm(business=self.business)

        self.assertEqual(
            list(form.fields),
            ["canonical_material", "percentage", "original_text", "source"],
        )
        self.assertNotIn("business", form.fields)
        self.assertNotIn("product", form.fields)
        self.assertNotIn("confirmation_state", form.fields)
        self.assertEqual(form.fields["percentage"].widget.attrs["min"], 1)
        self.assertEqual(form.fields["percentage"].widget.attrs["max"], 100)

    def test_form_validates_optional_percentage_and_source(self):
        form = ProductMaterialFactForm(
            data={
                "canonical_material": "Cotton",
                "percentage": "70",
                "original_text": "70% cotton",
                "source": ProductMaterialFact.Source.DESCRIPTION,
            },
            business=self.business,
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["percentage"], 70)

    def test_form_rejects_existing_fact_from_another_business(self):
        other_product = Product.objects.create(
            business=self.other_business,
            name="Other dress",
            description="Other description.",
        )
        fact = ProductMaterialFact.objects.create(
            business=self.other_business,
            product=other_product,
            canonical_material="Silk",
            original_text="Silk",
            source=ProductMaterialFact.Source.MANUAL,
        )
        form = ProductMaterialFactForm(
            data={
                "canonical_material": "Silk",
                "percentage": "",
                "original_text": "Silk",
                "source": ProductMaterialFact.Source.MANUAL,
            },
            instance=fact,
            business=self.business,
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Material fact must belong to the active Business.",
            form.non_field_errors(),
        )

    def test_bound_empty_extra_form_is_ignored(self):
        form = ProductMaterialFactForm(
            data={
                "materials-0-canonical_material": "",
                "materials-0-percentage": "",
                "materials-0-original_text": "",
                "materials-0-source": ProductMaterialFact.Source.MANUAL,
            },
            prefix="materials-0",
            business=self.business,
        )

        self.assertFalse(form.has_changed())


class MaterialCandidateTransferTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="material-transfer-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(owner=self.owner, name="Studio")
        source_product = Product.objects.create(
            business=self.business,
            name="Material source",
            description="Stored material vocabulary.",
        )
        ProductMaterialFact.objects.create(
            business=self.business,
            product=source_product,
            canonical_material="Cotton",
            original_text="Cotton",
            source=ProductMaterialFact.Source.MANUAL,
        )

    @staticmethod
    def candidate_reference(canonical_value="Cotton"):
        return (
            "0:material:0:6:"
            f"{quote(canonical_value, safe='')}"
        )

    @staticmethod
    def transfer_data(description="Cotton"):
        return {
            "description": description,
            "materials-TOTAL_FORMS": "1",
            "materials-INITIAL_FORMS": "0",
            "materials-MIN_NUM_FORMS": "0",
            "materials-MAX_NUM_FORMS": "1000",
            "materials-0-canonical_material": "",
            "materials-0-percentage": "",
            "materials-0-original_text": "",
            "materials-0-source": ProductMaterialFact.Source.MANUAL,
        }

    def test_transfer_places_current_candidate_in_unsaved_material_row(self):
        fact_count = ProductMaterialFact.objects.count()

        transfer = transfer_material_candidate(
            data=self.transfer_data(),
            business=self.business,
            candidate_reference=self.candidate_reference(),
        )

        self.assertEqual(
            transfer.data["materials-0-canonical_material"],
            "Cotton",
        )
        self.assertEqual(transfer.data["materials-0-original_text"], "Cotton")
        self.assertEqual(
            transfer.data["materials-0-source"],
            ProductMaterialFact.Source.DESCRIPTION,
        )
        self.assertEqual(ProductMaterialFact.objects.count(), fact_count)

    def test_transfer_rejects_tampered_canonical_meaning(self):
        with self.assertRaisesMessage(
            ValidationError,
            "That candidate is no longer available.",
        ):
            transfer_material_candidate(
                data=self.transfer_data(),
                business=self.business,
                candidate_reference=self.candidate_reference("Silk"),
            )

    def test_transfer_rejects_missing_material_management_state(self):
        with self.assertRaisesMessage(
            ValidationError,
            "Material form state is invalid.",
        ):
            transfer_material_candidate(
                data={"description": "Cotton"},
                business=self.business,
                candidate_reference=self.candidate_reference(),
            )


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

    def test_inactive_product_type_and_alias_are_not_recognized(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Shirt",
            is_active=False,
        )
        BusinessProductTypeAlias.objects.create(
            business=self.business,
            product_type=product_type,
            alias="party shirt",
        )

        result = recognize_product_types_for_business(
            "party shirt",
            self.business,
        )

        self.assertEqual(result.candidates, ())


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

    def test_inactive_tag_and_alias_are_not_recognized(self):
        tag = BusinessTag.objects.create(
            business=self.business,
            name="Party",
            is_active=False,
        )
        BusinessTagAlias.objects.create(
            business=self.business,
            tag=tag,
            alias="partywear",
        )

        result = recognize_tags_for_business("partywear", self.business)

        self.assertEqual(result.candidates, ())


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

    def test_product_accepts_one_owned_product_type(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )

        product = Product.objects.create(
            business=self.business,
            product_type=product_type,
            name="Black trousers",
            description="Classic black trousers.",
        )

        self.assertEqual(product.product_type, product_type)
        self.assertEqual(product_type.products.get(), product)

    def test_product_rejects_product_type_from_another_business(self):
        other_product_type = BusinessProductType.objects.create(
            business=self.other_business,
            name="Private type",
        )
        product = Product(
            business=self.business,
            product_type=other_product_type,
            name="Black trousers",
            description="Classic black trousers.",
        )

        with self.assertRaises(ValidationError):
            product.full_clean()
        with self.assertRaises(ValidationError):
            product.save()

        self.assertFalse(Product.objects.exists())

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


class ProductTagModelTests(TestCase):
    def setUp(self):
        owner = get_user_model().objects.create_user(
            email="product-tag-owner@example.com",
            password="test-password",
        )
        other_owner = get_user_model().objects.create_user(
            email="product-tag-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(owner=owner, name="Seller Studio")
        self.other_business = Business.objects.create(
            owner=other_owner,
            name="Other Studio",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
        )
        self.other_product = Product.objects.create(
            business=self.other_business,
            name="Private dress",
            description="Private description.",
        )
        self.tag = BusinessTag.objects.create(
            business=self.business,
            name="Classic",
        )
        self.other_tag = BusinessTag.objects.create(
            business=self.other_business,
            name="Private",
        )

    def test_product_tag_is_business_owned_confirmed_association(self):
        link = ProductTag.objects.create(
            business=self.business,
            product=self.product,
            tag=self.tag,
        )

        self.assertEqual(self.product.tags.get(), self.tag)
        self.assertEqual(self.tag.products.get(), self.product)
        self.assertEqual(self.business.product_tag_links.get(), link)

    def test_product_tag_rejects_cross_business_product_or_tag(self):
        wrong_product = ProductTag(
            business=self.business,
            product=self.other_product,
            tag=self.tag,
        )
        wrong_tag = ProductTag(
            business=self.business,
            product=self.product,
            tag=self.other_tag,
        )

        for link in (wrong_product, wrong_tag):
            with self.subTest(link=link):
                with self.assertRaises(ValidationError):
                    link.full_clean()
                with self.assertRaises(ValidationError):
                    link.save()

        self.assertFalse(ProductTag.objects.exists())

    def test_product_tag_is_unique_per_product(self):
        ProductTag.objects.create(
            business=self.business,
            product=self.product,
            tag=self.tag,
        )
        duplicate = ProductTag(
            business=self.business,
            product=self.product,
            tag=self.tag,
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()


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
        self.size = size_value(self.business, "M")
        self.large_size = size_value(self.business, "L")
        self.color = color_value(self.business, "Black")
        self.other_size = size_value(self.other_business, "M")
        self.other_color = color_value(self.other_business, "Black")

    def test_choice_belongs_to_business_and_product(self):
        choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
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
                    size=self.size,
                    color=self.color,
                )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductChoice.objects.create(
                    business=self.business,
                    size=self.size,
                    color=self.color,
                )

    def test_choice_requires_size_and_color_references(self):
        for field_name in ("size", "color"):
            with self.subTest(field_name=field_name):
                choice = ProductChoice(
                    business=self.business,
                    product=self.product,
                    size=self.size,
                    color=self.color,
                )
                setattr(choice, field_name, None)

                with self.assertRaises(ValidationError):
                    choice.full_clean()

    def test_choice_quantity_accepts_zero_and_rejects_negative_values(self):
        choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=0,
        )

        self.assertEqual(choice.quantity, 0)

        invalid_choice = ProductChoice(
            business=self.business,
            product=self.product,
            size=self.large_size,
            color=self.color,
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
            size=self.size,
            color=self.color,
            is_active=False,
        )

        self.assertFalse(choice.is_active)

    def test_choice_requires_matching_product_business(self):
        choice = ProductChoice(
            business=self.business,
            product=self.other_product,
            size=self.size,
            color=self.color,
        )

        with self.assertRaises(ValidationError):
            choice.full_clean()
        with self.assertRaises(ValidationError):
            choice.save()

    def test_choice_rejects_cross_business_size_and_color_references(self):
        wrong_size = ProductChoice(
            business=self.business,
            product=self.product,
            size=self.other_size,
            color=self.color,
        )
        wrong_color = ProductChoice(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.other_color,
        )

        for choice in (wrong_size, wrong_color):
            with self.assertRaises(ValidationError):
                choice.full_clean()
            with self.assertRaises(ValidationError):
                choice.save()

    def test_duplicate_choices_with_the_same_canonical_values_are_allowed(self):
        first_choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=1,
            is_active=False,
        )
        second_choice = ProductChoice(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=3,
        )

        second_choice.full_clean()
        second_choice.save()

        self.assertNotEqual(first_choice.pk, second_choice.pk)
        self.assertEqual(ProductChoice.objects.filter(product=self.product).count(), 2)
        self.assertEqual(second_choice.size, self.size)
        self.assertEqual(second_choice.color, self.color)
        self.assertEqual(first_choice.quantity, 1)
        self.assertEqual(second_choice.quantity, 3)
        self.assertFalse(first_choice.is_active)
        self.assertTrue(second_choice.is_active)

    def test_same_size_color_combination_is_allowed_on_another_product(self):
        ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
        )

        same_business_choice = ProductChoice.objects.create(
            business=self.business,
            product=self.second_product,
            size=self.size,
            color=self.color,
        )
        other_business_choice = ProductChoice.objects.create(
            business=self.other_business,
            product=self.other_product,
            size=self.other_size,
            color=self.other_color,
        )

        self.assertEqual(ProductChoice.objects.count(), 3)
        self.assertEqual(same_business_choice.product, self.second_product)
        self.assertEqual(other_business_choice.business, self.other_business)

    def test_product_deletion_is_protected_when_choice_exists(self):
        ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
        )

        with self.assertRaises(ProtectedError):
            self.product.delete()

    def test_business_deletion_is_protected_when_choice_exists(self):
        ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
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
            size=self.size,
            color=self.color,
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
        self.product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        self.tag = BusinessTag.objects.create(
            business=self.business,
            name="Classic",
        )
        self.other_product_type = BusinessProductType.objects.create(
            business=self.other_business,
            name="Private type",
        )
        self.other_tag = BusinessTag.objects.create(
            business=self.other_business,
            name="Private tag",
        )

    def test_form_exposes_only_approved_product_fields(self):
        form = ProductForm(business=self.business)

        self.assertEqual(
            list(form.fields),
            ["name", "description", "product_type", "tags", "lifecycle"],
        )

    def test_form_classification_choices_are_business_scoped(self):
        form = ProductForm(business=self.business)

        self.assertEqual(
            list(form.fields["product_type"].queryset),
            [self.product_type],
        )
        self.assertEqual(list(form.fields["tags"].queryset), [self.tag])
        self.assertNotIn(
            self.other_product_type,
            form.fields["product_type"].queryset,
        )
        self.assertNotIn(self.other_tag, form.fields["tags"].queryset)

    def test_form_hides_inactive_classification_from_new_products(self):
        self.product_type.is_active = False
        self.product_type.save(update_fields=["is_active"])
        self.tag.is_active = False
        self.tag.save(update_fields=["is_active"])

        form = ProductForm(business=self.business)

        self.assertNotIn(self.product_type, form.fields["product_type"].queryset)
        self.assertNotIn(self.tag, form.fields["tags"].queryset)

    def test_form_preserves_inactive_existing_classification_for_edit(self):
        product = Product.objects.create(
            business=self.business,
            product_type=self.product_type,
            name="Party shirt",
            description="Party shirt.",
        )
        ProductTag.objects.create(
            business=self.business,
            product=product,
            tag=self.tag,
        )
        self.product_type.is_active = False
        self.product_type.save(update_fields=["is_active"])
        self.tag.is_active = False
        self.tag.save(update_fields=["is_active"])

        form = ProductForm(instance=product, business=self.business)

        self.assertIn(self.product_type, form.fields["product_type"].queryset)
        self.assertIn(self.tag, form.fields["tags"].queryset)

    def test_form_rejects_cross_business_classification_values(self):
        form = ProductForm(
            data={
                "name": "Black trousers",
                "description": "Classic black trousers.",
                "product_type": self.other_product_type.pk,
                "tags": [self.other_tag.pk],
                "lifecycle": Product.Lifecycle.DRAFT,
            },
            business=self.business,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("product_type", form.errors)
        self.assertIn("tags", form.errors)

    def test_form_prepares_existing_owned_classification_for_edit(self):
        product = Product.objects.create(
            business=self.business,
            product_type=self.product_type,
            name="Black trousers",
            description="Classic black trousers.",
        )
        ProductTag.objects.create(
            business=self.business,
            product=product,
            tag=self.tag,
        )

        form = ProductForm(instance=product, business=self.business)

        self.assertEqual(form["product_type"].value(), self.product_type.pk)
        self.assertEqual(list(form["tags"].value()), [self.tag.pk])

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
            },
            business=self.business,
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
    def setUp(self):
        owner = get_user_model().objects.create_user(
            email="choice-form-owner@example.com",
            password="test-password",
        )
        other_owner = get_user_model().objects.create_user(
            email="choice-form-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(owner=owner, name="Seller Studio")
        self.other_business = Business.objects.create(
            owner=other_owner,
            name="Other Studio",
        )
        self.size = size_value(self.business)
        self.color = color_value(self.business)
        self.other_size = size_value(self.other_business, "L")
        self.other_color = color_value(self.other_business, "Red")

    def test_form_exposes_only_choice_owned_fields(self):
        form = ProductChoiceForm(business=self.business)

        self.assertEqual(
            list(form.fields),
            ["size", "color", "quantity", "is_active"],
        )

    def test_form_ignores_submitted_business_and_product(self):
        form = ProductChoiceForm(
            data={
                "business": 999,
                "product": 999,
                "size": self.size.pk,
                "color": self.color.pk,
                "quantity": 2,
                "is_active": True,
            },
            business=self.business,
        )

        self.assertTrue(form.is_valid())
        choice = form.save(commit=False)
        self.assertIsNone(choice.business_id)
        self.assertIsNone(choice.product_id)

    def test_form_dropdowns_include_only_active_values_from_the_business(self):
        inactive_size = size_value(self.business, "XL")
        inactive_size.is_active = False
        inactive_size.save(update_fields=["is_active"])

        form = ProductChoiceForm(business=self.business)

        self.assertEqual(list(form.fields["size"].queryset), [self.size])
        self.assertEqual(list(form.fields["color"].queryset), [self.color])
        self.assertNotIn(self.other_size, form.fields["size"].queryset)

    def test_form_rejects_cross_business_vocabulary_ids(self):
        form = ProductChoiceForm(
            data={
                "size": self.other_size.pk,
                "color": self.other_color.pk,
                "quantity": 2,
                "is_active": True,
            },
            business=self.business,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("size", form.errors)
        self.assertIn("color", form.errors)


class ProductChoiceFormSetTests(TestCase):
    prefix = "choices"

    def setUp(self):
        owner = get_user_model().objects.create_user(
            email="choice-formset-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(owner=owner, name="Seller Studio")
        self.size = size_value(self.business)
        self.color = color_value(self.business)

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
            form_kwargs={"business": self.business},
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
                "size": str(self.size.pk),
                "color": "",
                "quantity": "2",
                "is_active": "on",
            }
        ]

        formset = self.build_formset(product, rows)

        self.assertFalse(formset.is_valid())
        self.assertIn("color", formset.forms[0].errors)
        self.assertEqual(
            formset.forms[0].data[f"{self.prefix}-0-size"],
            str(self.size.pk),
        )

    def test_normalized_duplicate_choice_rows_are_valid(self):
        product = Product(
            business=self.business,
            name="Active trousers",
            description="Active description.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        rows = [
            {
                "size": str(self.size.pk),
                "color": str(self.color.pk),
                "quantity": "1",
                "is_active": "on",
            },
            {
                "size": str(self.size.pk),
                "color": str(self.color.pk),
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
            size=self.size,
            color=self.color,
            quantity=1,
        )
        rows = [
            {
                "id": str(choice.pk),
                "size": str(choice.size_id),
                "color": str(choice.color_id),
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
    material_prefix = "materials"

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
        self.size = size_value(self.business, "M")
        self.large_size = size_value(self.business, "L")
        self.color = color_value(self.business, "Black")
        self.other_size = size_value(self.other_business, "L")
        self.other_color = color_value(self.other_business, "Red")
        self.product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        self.second_product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Shirt",
        )
        self.tag = BusinessTag.objects.create(
            business=self.business,
            name="Classic",
        )
        self.second_tag = BusinessTag.objects.create(
            business=self.business,
            name="Pockets",
        )
        self.other_product_type = BusinessProductType.objects.create(
            business=self.other_business,
            name="Private type",
        )
        self.other_tag = BusinessTag.objects.create(
            business=self.other_business,
            name="Private tag",
        )

    def bundle_data(
        self,
        rows,
        *,
        lifecycle=Product.Lifecycle.ACTIVE,
        initial_forms=0,
        name="Black trousers",
        product_type="",
        tags=(),
        material_rows=(),
        material_initial_forms=0,
    ):
        data = {
            "name": name,
            "description": "Classic black trousers.",
            "product_type": str(product_type or ""),
            "tags": [str(tag) for tag in tags],
            "lifecycle": lifecycle,
            f"{self.prefix}-TOTAL_FORMS": str(len(rows)),
            f"{self.prefix}-INITIAL_FORMS": str(initial_forms),
            f"{self.prefix}-MIN_NUM_FORMS": "0",
            f"{self.prefix}-MAX_NUM_FORMS": "1000",
            f"{self.material_prefix}-TOTAL_FORMS": str(len(material_rows)),
            f"{self.material_prefix}-INITIAL_FORMS": str(material_initial_forms),
            f"{self.material_prefix}-MIN_NUM_FORMS": "0",
            f"{self.material_prefix}-MAX_NUM_FORMS": "1000",
        }
        for index, row in enumerate(rows):
            for field, value in row.items():
                data[f"{self.prefix}-{index}-{field}"] = value
        for index, row in enumerate(material_rows):
            for field, value in row.items():
                data[f"{self.material_prefix}-{index}-{field}"] = value
        return data

    def active_choice_row(self, **overrides):
        row = {
            "size": str(self.size.pk),
            "color": str(self.color.pk),
            "quantity": "2",
            "is_active": "on",
        }
        row.update(overrides)
        return row

    @staticmethod
    def material_row(**overrides):
        row = {
            "canonical_material": "Cotton",
            "percentage": "70",
            "original_text": "70% cotton",
            "source": ProductMaterialFact.Source.DESCRIPTION,
        }
        row.update(overrides)
        return row

    def test_valid_create_assigns_ownership_and_saves_one_bundle(self):
        bundle = ProductBundle(
            business=self.business,
            data=self.bundle_data(
                [self.active_choice_row()],
                product_type=self.product_type.pk,
                tags=(self.tag.pk, self.second_tag.pk),
            ),
        )

        self.assertTrue(bundle.is_valid())
        product = bundle.save()

        self.assertEqual(product.business, self.business)
        self.assertEqual(product.lifecycle, Product.Lifecycle.ACTIVE)
        self.assertEqual(product.product_type, self.product_type)
        self.assertEqual(set(product.tags.all()), {self.tag, self.second_tag})
        self.assertTrue(
            all(
                link.business == self.business
                for link in ProductTag.objects.filter(product=product)
            )
        )
        choice = ProductChoice.objects.get()
        self.assertEqual(choice.business, self.business)
        self.assertEqual(choice.product, product)
        self.assertEqual(choice.size, self.size)
        self.assertEqual(choice.color, self.color)
        self.assertEqual(choice.quantity, 2)

    def test_valid_create_saves_explicit_confirmed_material_fact(self):
        bundle = ProductBundle(
            business=self.business,
            data=self.bundle_data(
                [self.active_choice_row()],
                material_rows=[self.material_row()],
            ),
        )

        self.assertTrue(bundle.is_valid(), bundle.material_formset.errors)
        product = bundle.save()

        fact = product.material_facts.get()
        self.assertEqual(fact.business, self.business)
        self.assertEqual(fact.canonical_material, "Cotton")
        self.assertEqual(fact.percentage, 70)
        self.assertEqual(fact.original_text, "70% cotton")
        self.assertEqual(fact.source, ProductMaterialFact.Source.DESCRIPTION)
        self.assertEqual(
            fact.confirmation_state,
            ProductMaterialFact.ConfirmationState.CONFIRMED,
        )

    def test_invalid_material_does_not_partially_persist_bundle(self):
        bundle = ProductBundle(
            business=self.business,
            data=self.bundle_data(
                [self.active_choice_row()],
                tags=(self.tag.pk,),
                material_rows=[self.material_row(percentage="101")],
            ),
        )

        self.assertFalse(bundle.is_valid())
        self.assertIn("percentage", bundle.material_formset.forms[0].errors)
        with self.assertRaisesMessage(
            ValueError,
            "Cannot save an invalid Product bundle.",
        ):
            bundle.save()

        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)
        self.assertEqual(ProductTag.objects.count(), 0)
        self.assertEqual(ProductMaterialFact.objects.count(), 0)

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
        self.assertEqual(ProductTag.objects.count(), 0)

    def test_cross_business_classification_is_rejected_without_writes(self):
        bundle = ProductBundle(
            business=self.business,
            data=self.bundle_data(
                [self.active_choice_row()],
                product_type=self.other_product_type.pk,
                tags=(self.other_tag.pk,),
            ),
        )

        self.assertFalse(bundle.is_valid())
        self.assertIn("product_type", bundle.product_form.errors)
        self.assertIn("tags", bundle.product_form.errors)
        with self.assertRaisesMessage(
            ValueError,
            "Cannot save an invalid Product bundle.",
        ):
            bundle.save()

        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)
        self.assertEqual(ProductTag.objects.count(), 0)

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

    def test_tag_save_failure_rolls_back_product_and_choices(self):
        bundle = ProductBundle(
            business=self.business,
            data=self.bundle_data(
                [self.active_choice_row()],
                product_type=self.product_type.pk,
                tags=(self.tag.pk,),
            ),
        )
        self.assertTrue(bundle.is_valid())

        with patch(
            "catalog.product_bundles.ProductTag.save",
            side_effect=IntegrityError("simulated tag write failure"),
        ):
            with self.assertRaisesMessage(
                IntegrityError,
                "simulated tag write failure",
            ):
                bundle.save()

        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)
        self.assertEqual(ProductTag.objects.count(), 0)

    def test_material_save_failure_rolls_back_product_choices_and_tags(self):
        bundle = ProductBundle(
            business=self.business,
            data=self.bundle_data(
                [self.active_choice_row()],
                tags=(self.tag.pk,),
                material_rows=[self.material_row()],
            ),
        )
        self.assertTrue(bundle.is_valid())

        with patch(
            "catalog.product_bundles.ProductMaterialFact.save",
            side_effect=IntegrityError("simulated material write failure"),
        ):
            with self.assertRaisesMessage(
                IntegrityError,
                "simulated material write failure",
            ):
                bundle.save()

        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)
        self.assertEqual(ProductTag.objects.count(), 0)
        self.assertEqual(ProductMaterialFact.objects.count(), 0)

    def test_normalized_duplicate_rows_persist_as_distinct_choices(self):
        rows = [
            self.active_choice_row(quantity="1"),
            self.active_choice_row(quantity="3"),
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
            size=self.size,
            color=self.color,
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
            size=self.other_size,
            color=self.other_color,
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
            product_type=self.product_type,
            name="Old trousers",
            description="Old description.",
            lifecycle=Product.Lifecycle.DRAFT,
        )
        choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=self.size,
            color=self.color,
            quantity=1,
        )
        ProductTag.objects.create(
            business=self.business,
            product=product,
            tag=self.tag,
        )
        row = self.active_choice_row(
            id=str(choice.pk),
            size=str(self.large_size.pk),
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
                product_type=self.second_product_type.pk,
                tags=(self.second_tag.pk,),
            ),
        )

        self.assertTrue(bundle.is_valid())
        bundle.save()

        product.refresh_from_db()
        choice.refresh_from_db()
        self.assertEqual(product.name, "Updated trousers")
        self.assertEqual(product.lifecycle, Product.Lifecycle.ACTIVE)
        self.assertEqual(product.product_type, self.second_product_type)
        self.assertEqual(list(product.tags.all()), [self.second_tag])
        self.assertEqual(choice.size, self.large_size)
        self.assertEqual(choice.quantity, 5)

    def test_valid_update_can_remove_type_and_all_tags(self):
        product = Product.objects.create(
            business=self.business,
            product_type=self.product_type,
            name="Draft trousers",
            description="Draft description.",
        )
        ProductTag.objects.create(
            business=self.business,
            product=product,
            tag=self.tag,
        )
        bundle = ProductBundle(
            business=self.business,
            instance=product,
            data=self.bundle_data(
                [{}],
                lifecycle=Product.Lifecycle.DRAFT,
                product_type="",
                tags=(),
            ),
        )

        self.assertTrue(bundle.is_valid())
        bundle.save()

        product.refresh_from_db()
        self.assertIsNone(product.product_type)
        self.assertFalse(product.tags.exists())
        self.assertFalse(ProductTag.objects.filter(product=product).exists())

    def test_valid_update_corrects_and_removes_material_facts(self):
        product = Product.objects.create(
            business=self.business,
            name="Draft trousers",
            description="Draft description.",
        )
        corrected_fact = ProductMaterialFact.objects.create(
            business=self.business,
            product=product,
            canonical_material="Cottn",
            original_text="cottn",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )
        removed_fact = ProductMaterialFact.objects.create(
            business=self.business,
            product=product,
            canonical_material="Silk",
            original_text="silk",
            source=ProductMaterialFact.Source.MANUAL,
        )
        material_rows = [
            self.material_row(
                id=str(corrected_fact.pk),
                canonical_material="Cotton",
                percentage="80",
                original_text="80% cotton",
            ),
            self.material_row(
                id=str(removed_fact.pk),
                canonical_material="Silk",
                percentage="",
                original_text="silk",
                source=ProductMaterialFact.Source.MANUAL,
                DELETE="on",
            ),
        ]
        bundle = ProductBundle(
            business=self.business,
            instance=product,
            data=self.bundle_data(
                [{}],
                lifecycle=Product.Lifecycle.DRAFT,
                material_rows=material_rows,
                material_initial_forms=2,
            ),
        )

        self.assertTrue(bundle.is_valid(), bundle.material_formset.errors)
        bundle.save()

        corrected_fact.refresh_from_db()
        self.assertEqual(corrected_fact.canonical_material, "Cotton")
        self.assertEqual(corrected_fact.percentage, 80)
        self.assertEqual(corrected_fact.original_text, "80% cotton")
        self.assertFalse(ProductMaterialFact.objects.filter(pk=removed_fact.pk).exists())

    def test_forged_material_id_cannot_mutate_another_business_fact(self):
        product = Product.objects.create(
            business=self.business,
            name="Owned trousers",
            description="Owned description.",
        )
        owned_fact = ProductMaterialFact.objects.create(
            business=self.business,
            product=product,
            canonical_material="Cotton",
            original_text="Cotton",
            source=ProductMaterialFact.Source.MANUAL,
        )
        other_product = Product.objects.create(
            business=self.other_business,
            name="Other dress",
            description="Other description.",
        )
        other_fact = ProductMaterialFact.objects.create(
            business=self.other_business,
            product=other_product,
            canonical_material="Silk",
            original_text="Silk",
            source=ProductMaterialFact.Source.MANUAL,
        )
        bundle = ProductBundle(
            business=self.business,
            instance=product,
            data=self.bundle_data(
                [{}],
                lifecycle=Product.Lifecycle.DRAFT,
                material_rows=[
                    self.material_row(
                        id=str(other_fact.pk),
                        canonical_material="Leaked",
                    )
                ],
                material_initial_forms=1,
            ),
        )

        self.assertFalse(bundle.is_valid())
        self.assertIn("id", bundle.material_formset.forms[0].errors)
        owned_fact.refresh_from_db()
        other_fact.refresh_from_db()
        self.assertEqual(owned_fact.canonical_material, "Cotton")
        self.assertEqual(other_fact.canonical_material, "Silk")

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
            size=self.size,
            color=self.color,
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
            size=self.size,
            color=self.color,
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
        self.assertContains(response, "Manage product vocabulary")
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


class ChoiceVocabularyViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="vocabulary-view-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="vocabulary-view-other@example.com",
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
        self.url = reverse("catalog:choice_vocabulary")

    def test_vocabulary_page_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_vocabulary_page_groups_owned_aliases_and_includes_inactive_values(self):
        size = size_value(self.business, "M")
        inactive_color = color_value(self.business, "შავი")
        inactive_color.is_active = False
        inactive_color.save(update_fields=["is_active"])
        BusinessSizeAlias.objects.create(
            business=self.business,
            size=size,
            alias="M-ზომა",
        )
        BusinessColorAlias.objects.create(
            business=self.business,
            color=inactive_color,
            alias="Black",
        )
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="პერანგი",
            is_active=False,
        )
        BusinessProductTypeAlias.objects.create(
            business=self.business,
            product_type=product_type,
            alias="Shirt",
        )
        tag = BusinessTag.objects.create(
            business=self.business,
            name="საღამოს",
        )
        BusinessTagAlias.objects.create(
            business=self.business,
            tag=tag,
            alias="Party",
        )
        other_size = size_value(self.other_business, "PRIVATE-OTHER-SIZE")
        BusinessSizeAlias.objects.create(
            business=self.other_business,
            size=other_size,
            alias="PRIVATE-OTHER-ALIAS",
        )
        BusinessProductType.objects.create(
            business=self.other_business,
            name="PRIVATE-OTHER-TYPE",
        )
        BusinessTag.objects.create(
            business=self.other_business,
            name="PRIVATE-OTHER-TAG",
        )
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/choice_vocabulary.html")
        self.assertContains(response, "Product vocabulary")
        self.assertContains(response, "Product types")
        self.assertContains(response, "Tags")
        self.assertContains(response, "M-ზომა")
        self.assertContains(response, "Black")
        self.assertContains(response, "Shirt")
        self.assertContains(response, "Party")
        self.assertContains(response, "Inactive")
        self.assertNotContains(response, "PRIVATE-OTHER-SIZE")
        self.assertNotContains(response, "PRIVATE-OTHER-ALIAS")
        self.assertNotContains(response, "PRIVATE-OTHER-TYPE")
        self.assertNotContains(response, "PRIVATE-OTHER-TAG")

    def test_vocabulary_page_adds_canonical_with_grouped_aliases(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {
                "add-size-name": " M ",
                "add-size-aliases": "M-ზომა, M size",
                "intent": "add_size_vocabulary",
            },
        )

        self.assertRedirects(response, self.url)
        size = BusinessSize.objects.get(business=self.business, name="M")
        self.assertEqual(
            set(size.aliases.values_list("alias", flat=True)),
            {"M-ზომა", "M size"},
        )

    def test_vocabulary_page_adds_product_type_and_tag_with_aliases(self):
        self.client.force_login(self.owner)

        type_response = self.client.post(
            self.url,
            {
                "add-product_type-name": " პერანგი ",
                "add-product_type-aliases": "Shirt, party shirt",
                "intent": "add_product_type_vocabulary",
            },
        )
        tag_response = self.client.post(
            self.url,
            {
                "add-tag-name": " საღამოს ",
                "add-tag-aliases": "Party, partywear",
                "intent": "add_tag_vocabulary",
            },
        )

        self.assertRedirects(type_response, self.url)
        self.assertRedirects(tag_response, self.url)
        product_type = BusinessProductType.objects.get(
            business=self.business,
            name="პერანგი",
        )
        tag = BusinessTag.objects.get(
            business=self.business,
            name="საღამოს",
        )
        self.assertEqual(
            set(product_type.aliases.values_list("alias", flat=True)),
            {"Shirt", "party shirt"},
        )
        self.assertEqual(
            set(tag.aliases.values_list("alias", flat=True)),
            {"Party", "partywear"},
        )

    def test_vocabulary_page_updates_taxonomy_without_changing_product_truth(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Shirt",
        )
        tag = BusinessTag.objects.create(
            business=self.business,
            name="Party",
        )
        product = Product.objects.create(
            business=self.business,
            product_type=product_type,
            name="Party shirt",
            description="Party shirt.",
        )
        ProductTag.objects.create(
            business=self.business,
            product=product,
            tag=tag,
        )
        self.client.force_login(self.owner)

        type_response = self.client.post(
            self.url,
            {
                f"edit-product_type-{product_type.pk}-name": "პერანგი",
                f"edit-product_type-{product_type.pk}-aliases": "Shirt",
                "intent": f"update_vocabulary:product_type:{product_type.pk}",
            },
        )
        tag_response = self.client.post(
            self.url,
            {
                f"edit-tag-{tag.pk}-name": "საღამოს",
                f"edit-tag-{tag.pk}-aliases": "Party",
                "intent": f"update_vocabulary:tag:{tag.pk}",
            },
        )

        self.assertRedirects(type_response, self.url)
        self.assertRedirects(tag_response, self.url)
        product.refresh_from_db()
        product_type.refresh_from_db()
        tag.refresh_from_db()
        self.assertEqual(product.product_type_id, product_type.pk)
        self.assertTrue(
            ProductTag.objects.filter(product=product, tag=tag).exists()
        )
        self.assertEqual(product_type.name, "პერანგი")
        self.assertEqual(tag.name, "საღამოს")
        self.assertFalse(product_type.is_active)
        self.assertFalse(tag.is_active)

    def test_vocabulary_page_cannot_update_another_business_taxonomy(self):
        other_type = BusinessProductType.objects.create(
            business=self.other_business,
            name="Private type",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {
                f"edit-product_type-{other_type.pk}-name": "Changed",
                f"edit-product_type-{other_type.pk}-aliases": "Private",
                f"edit-product_type-{other_type.pk}-is_active": "on",
                "intent": f"update_vocabulary:product_type:{other_type.pk}",
            },
        )

        self.assertEqual(response.status_code, 404)
        other_type.refresh_from_db()
        self.assertEqual(other_type.name, "Private type")
        self.assertFalse(other_type.aliases.exists())

    def test_vocabulary_page_updates_entry_without_changing_choice_identity(self):
        size = size_value(self.business, "M")
        color = color_value(self.business, "Black")
        BusinessSizeAlias.objects.create(
            business=self.business,
            size=size,
            alias="M size",
        )
        product = Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
        )
        choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=size,
            color=color,
            quantity=5,
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {
                f"edit-size-{size.pk}-name": "Medium",
                f"edit-size-{size.pk}-aliases": "M, M-ზომა",
                "intent": f"update_vocabulary:size:{size.pk}",
            },
        )

        self.assertRedirects(response, self.url)
        size.refresh_from_db()
        choice.refresh_from_db()
        self.assertEqual(size.name, "Medium")
        self.assertFalse(size.is_active)
        self.assertEqual(
            set(size.aliases.values_list("alias", flat=True)),
            {"M", "M-ზომა"},
        )
        self.assertEqual(choice.size_id, size.pk)
        self.assertEqual(choice.quantity, 5)

    def test_vocabulary_page_reactivates_inactive_entry(self):
        color = color_value(self.business, "Black")
        color.is_active = False
        color.save(update_fields=["is_active"])
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {
                f"edit-color-{color.pk}-name": "Black",
                f"edit-color-{color.pk}-aliases": "შავი",
                f"edit-color-{color.pk}-is_active": "on",
                "intent": f"update_vocabulary:color:{color.pk}",
            },
        )

        self.assertRedirects(response, self.url)
        color.refresh_from_db()
        self.assertTrue(color.is_active)
        self.assertEqual(
            list(color.aliases.values_list("alias", flat=True)),
            ["შავი"],
        )

    def test_vocabulary_page_rolls_back_conflicting_alias_update(self):
        medium = size_value(self.business, "M")
        small = size_value(self.business, "S")
        BusinessSizeAlias.objects.create(
            business=self.business,
            size=medium,
            alias="M size",
        )
        BusinessSizeAlias.objects.create(
            business=self.business,
            size=small,
            alias="Small",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {
                f"edit-size-{medium.pk}-name": "Medium",
                f"edit-size-{medium.pk}-aliases": "M-ზომა, Small",
                f"edit-size-{medium.pk}-is_active": "on",
                "intent": f"update_vocabulary:size:{medium.pk}",
            },
        )

        self.assertEqual(response.status_code, 200)
        bound_row = next(
            row
            for row in response.context["size_entries"]
            if row["entry"].pk == medium.pk
        )
        self.assertTrue(bound_row["form"].errors)
        medium.refresh_from_db()
        self.assertEqual(medium.name, "M")
        self.assertTrue(medium.is_active)
        self.assertEqual(
            list(medium.aliases.values_list("alias", flat=True)),
            ["M size"],
        )

    def test_vocabulary_page_cannot_update_another_business_entry(self):
        other_color = color_value(self.other_business, "Red")
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {
                f"edit-color-{other_color.pk}-name": "Blue",
                f"edit-color-{other_color.pk}-aliases": "ლურჯი",
                f"edit-color-{other_color.pk}-is_active": "on",
                "intent": f"update_vocabulary:color:{other_color.pk}",
            },
        )

        self.assertEqual(response.status_code, 404)
        other_color.refresh_from_db()
        self.assertEqual(other_color.name, "Red")
        self.assertFalse(other_color.aliases.exists())

    def test_vocabulary_mutation_without_business_is_blocked(self):
        seller_without_business = get_user_model().objects.create_user(
            email="vocabulary-view-no-business@example.com",
            password="test-password",
        )
        self.client.force_login(seller_without_business)

        response = self.client.post(
            self.url,
            {
                "add-color-name": "შავი",
                "add-color-aliases": "Black",
                "intent": "add_color_vocabulary",
            },
        )

        self.assertEqual(response.status_code, 409)
        self.assertContains(
            response,
            "No business workspace yet.",
            status_code=409,
        )
        self.assertFalse(BusinessColor.objects.filter(name="შავი").exists())

    def test_vocabulary_page_preserves_safe_return_path(self):
        self.client.force_login(self.owner)
        return_url = f"{reverse('catalog:product_list')}?from=vocabulary"

        response = self.client.get(self.url, {"next": return_url})

        self.assertEqual(response.context["return_url"], return_url)
        self.assertContains(response, f'href="{return_url.replace("&", "&amp;")}"')

    def test_vocabulary_page_refuses_multiple_businesses_without_switcher(self):
        Business.objects.create(owner=self.owner, name="Second Studio")
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 409)
        self.assertContains(
            response,
            "Multiple business workspaces need an approved switcher",
            status_code=409,
        )


class ProductBundleViewTestMixin:
    choice_prefix = "choices"
    material_prefix = "materials"

    @staticmethod
    def transfer_intent(
        index,
        destination,
        span_start,
        span_end,
        canonical_value,
    ):
        return (
            f"transfer_choice_candidate:{index}:{destination.value}:"
            f"{span_start}:{span_end}:{quote(canonical_value, safe='')}"
        )

    @staticmethod
    def material_transfer_intent(
        index,
        span_start,
        span_end,
        canonical_value,
    ):
        return (
            f"transfer_material_candidate:{index}:material:"
            f"{span_start}:{span_end}:{quote(canonical_value, safe='')}"
        )

    def bundle_post_data(
        self,
        rows,
        *,
        lifecycle=Product.Lifecycle.ACTIVE,
        initial_forms=0,
        name="Black trousers",
        description="Classic black trousers.",
        product_type="",
        tags=(),
        material_rows=(),
        material_initial_forms=0,
    ):
        data = {
            "name": name,
            "description": description,
            "product_type": str(product_type or ""),
            "tags": [str(tag) for tag in tags],
            "lifecycle": lifecycle,
            f"{self.choice_prefix}-TOTAL_FORMS": str(len(rows)),
            f"{self.choice_prefix}-INITIAL_FORMS": str(initial_forms),
            f"{self.choice_prefix}-MIN_NUM_FORMS": "0",
            f"{self.choice_prefix}-MAX_NUM_FORMS": "1000",
            f"{self.material_prefix}-TOTAL_FORMS": str(len(material_rows)),
            f"{self.material_prefix}-INITIAL_FORMS": str(material_initial_forms),
            f"{self.material_prefix}-MIN_NUM_FORMS": "0",
            f"{self.material_prefix}-MAX_NUM_FORMS": "1000",
        }
        for index, row in enumerate(rows):
            for field, value in row.items():
                data[f"{self.choice_prefix}-{index}-{field}"] = value
        for index, row in enumerate(material_rows):
            for field, value in row.items():
                data[f"{self.material_prefix}-{index}-{field}"] = value
        return data

    def active_choice_row(self, **overrides):
        row = {
            "size": str(self.size.pk),
            "color": str(self.color.pk),
            "quantity": "2",
            "is_active": "on",
        }
        row.update(overrides)
        return row

    @staticmethod
    def material_row(**overrides):
        row = {
            "canonical_material": "Cotton",
            "percentage": "70",
            "original_text": "70% cotton",
            "source": ProductMaterialFact.Source.DESCRIPTION,
        }
        row.update(overrides)
        return row

    def seed_preview_vocabulary(
        self,
        business,
        *,
        product_type_name="Trousers",
        product_type_alias="pants",
        tag_name="Classic",
        material="Cotton",
        size="M",
        color="Black",
    ):
        product_type = BusinessProductType.objects.create(
            business=business,
            name=product_type_name,
        )
        BusinessProductTypeAlias.objects.create(
            business=business,
            product_type=product_type,
            alias=product_type_alias,
        )
        BusinessTag.objects.create(
            business=business,
            name=tag_name,
        )
        source_product = Product.objects.create(
            business=business,
            name=f"{product_type_name} preview source",
            description="Stored preview vocabulary.",
        )
        ProductMaterialFact.objects.create(
            business=business,
            product=source_product,
            canonical_material=material,
            original_text=material,
            source=ProductMaterialFact.Source.DESCRIPTION,
        )
        canonical_size = size_value(business, size)
        canonical_color = color_value(business, color)
        ProductChoice.objects.create(
            business=business,
            product=source_product,
            size=canonical_size,
            color=canonical_color,
        )
        return source_product


class ProductCreateViewTests(ProductBundleViewTestMixin, TestCase):
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
        self.size = size_value(self.business, "M")
        self.color = color_value(self.business, "Black")
        self.other_size = size_value(self.other_business, "L")
        self.other_color = color_value(self.other_business, "Red")
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
        self.assertContains(response, 'name="product_type"')
        self.assertIn("tags", response.context["form"].fields)
        self.assertContains(response, "Confirmed classification")
        self.assertContains(response, "Confirmed materials")
        self.assertContains(response, 'name="materials-TOTAL_FORMS"')
        self.assertContains(response, 'name="materials-0-canonical_material"')
        self.assertContains(response, 'name="materials-0-percentage"')
        self.assertContains(response, 'name="materials-0-original_text"')
        self.assertContains(response, 'name="materials-0-source"')
        self.assertContains(response, "Recognition candidates remain suggestions")
        self.assertContains(response, 'id="id_tags-label"')
        self.assertContains(
            response,
            'role="group" aria-labelledby="id_tags-label"',
        )
        self.assertContains(response, 'name="lifecycle"')
        self.assertContains(response, "Choices")
        self.assertContains(response, 'name="choices-TOTAL_FORMS"')
        self.assertContains(response, 'name="choices-0-size"')
        self.assertContains(response, 'name="choices-0-color"')
        self.assertContains(response, '<select name="choices-0-size"')
        self.assertContains(response, '<select name="choices-0-color"')
        self.assertNotContains(response, '<input type="text" name="choices-0-size"')
        self.assertNotContains(response, '<input type="text" name="choices-0-color"')
        self.assertContains(response, 'name="choices-0-quantity"')
        self.assertContains(response, 'name="choices-0-is_active"')
        self.assertContains(response, 'hx-post="."')
        self.assertContains(response, 'hx-trigger="input changed delay:600ms"')
        self.assertContains(response, 'hx-target="#recognition-preview-region"')
        self.assertContains(response, 'hx-include="closest form"')
        self.assertContains(response, "Known candidates appear automatically")
        self.assertContains(response, "django_htmx/htmx-2.min.js")
        self.assertNotContains(response, "Preview recognition")
        self.assertContains(response, "Create product")
        self.assertNotContains(response, 'name="business"')
        self.assertNotContains(response, 'name="materials-0-business"')
        self.assertNotContains(response, 'name="materials-0-product"')
        self.assertNotContains(response, 'name="materials-0-confirmation_state"')

    def test_product_create_classification_options_are_business_scoped(self):
        owned_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        owned_tag = BusinessTag.objects.create(
            business=self.business,
            name="Classic",
        )
        BusinessProductType.objects.create(
            business=self.other_business,
            name="PRIVATE-OTHER-TYPE",
        )
        BusinessTag.objects.create(
            business=self.other_business,
            name="PRIVATE-OTHER-TAG",
        )
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertContains(response, owned_type.name)
        self.assertContains(response, owned_tag.name)
        self.assertNotContains(response, "PRIVATE-OTHER-TYPE")
        self.assertNotContains(response, "PRIVATE-OTHER-TAG")

    def test_product_create_explicitly_saves_owned_type_and_tags(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        classic = BusinessTag.objects.create(
            business=self.business,
            name="Classic",
        )
        pockets = BusinessTag.objects.create(
            business=self.business,
            name="Pockets",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [self.active_choice_row()],
                product_type=product_type.pk,
                tags=(classic.pk, pockets.pk),
            ),
        )

        self.assertRedirects(response, self.list_url)
        product = Product.objects.get(name="Black trousers")
        self.assertEqual(product.product_type, product_type)
        self.assertEqual(set(product.tags.all()), {classic, pockets})
        self.assertEqual(
            set(product.tag_links.values_list("business_id", flat=True)),
            {self.business.pk},
        )

    def test_product_create_explicitly_saves_confirmed_material(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [self.active_choice_row()],
                material_rows=[self.material_row()],
            ),
        )

        self.assertRedirects(response, self.list_url)
        product = Product.objects.get(name="Black trousers")
        fact = product.material_facts.get()
        self.assertEqual(fact.business, self.business)
        self.assertEqual(fact.canonical_material, "Cotton")
        self.assertEqual(fact.percentage, 70)
        self.assertEqual(
            fact.confirmation_state,
            ProductMaterialFact.ConfirmationState.CONFIRMED,
        )

    def test_product_create_candidates_alone_do_not_attach_classification(self):
        self.seed_preview_vocabulary(self.business)
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [{}],
                lifecycle=Product.Lifecycle.DRAFT,
                name="Unclassified trousers",
                description="pants Classic",
            ),
        )

        self.assertRedirects(response, self.list_url)
        product = Product.objects.get(name="Unclassified trousers")
        self.assertIsNone(product.product_type)
        self.assertFalse(product.tags.exists())
        self.assertFalse(product.material_facts.exists())

    def test_product_create_rejects_cross_business_classification(self):
        other_type = BusinessProductType.objects.create(
            business=self.other_business,
            name="Private type",
        )
        other_tag = BusinessTag.objects.create(
            business=self.other_business,
            name="Private tag",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [self.active_choice_row()],
                product_type=other_type.pk,
                tags=(other_tag.pk,),
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice.", count=2)
        self.assertFalse(Product.objects.exists())
        self.assertFalse(ProductTag.objects.exists())

    def test_product_create_error_preserves_owned_classification_selection(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        tag = BusinessTag.objects.create(
            business=self.business,
            name="Classic",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [self.active_choice_row(color="")],
                description="Trousers Classic",
                product_type=product_type.pk,
                tags=(tag.pk,),
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"]["product_type"].value(),
            str(product_type.pk),
        )
        self.assertEqual(
            response.context["form"]["tags"].value(),
            [str(tag.pk)],
        )
        self.assertContains(response, "Recognized candidates")
        self.assertFalse(Product.objects.exists())
        self.assertFalse(ProductTag.objects.exists())

    def test_product_create_htmx_adds_size_and_aliases_without_saving_product(self):
        data = self.bundle_post_data(
            [self.active_choice_row()],
            name="Unsaved product",
            description="Unsaved description",
        )
        data.update(
            {
                "intent": "add_size_vocabulary",
                "size-vocabulary-name": "S",
                "size-vocabulary-aliases": "S-ზომა, S size",
            }
        )
        self.client.force_login(self.owner)

        response = self.client.post(self.url, data, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_choice_section.html")
        size = BusinessSize.objects.get(business=self.business, name="S")
        self.assertEqual(
            list(size.aliases.values_list("alias", flat=True)),
            ["S size", "S-ზომა"],
        )
        self.assertEqual(response.context["vocabulary_feedback"], 'Size "S" saved.')
        self.assertContains(response, ">S</option>")
        self.assertContains(response, f'value="{self.size.pk}" selected')
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_product_create_full_page_adds_color_and_preserves_unsaved_input(self):
        data = self.bundle_post_data(
            [self.active_choice_row()],
            name="Unsaved product",
            description="Unsaved description",
        )
        data.update(
            {
                "intent": "add_color_vocabulary",
                "color-vocabulary-name": "Black",
                "color-vocabulary-aliases": "შავი",
            }
        )
        self.client.force_login(self.owner)

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_form.html")
        color = BusinessColor.objects.get(business=self.business, name="Black")
        self.assertTrue(color.aliases.filter(alias="შავი").exists())
        self.assertContains(response, 'value="Unsaved product"')
        self.assertContains(response, "Unsaved description")
        self.assertEqual(
            response.context["vocabulary_feedback"],
            'Color "Black" saved.',
        )
        self.assertEqual(Product.objects.count(), 0)

    def test_product_create_rejects_cross_business_dropdown_values(self):
        self.client.force_login(self.owner)
        row = self.active_choice_row(
            size=str(self.other_size.pk),
            color=str(self.other_color.pk),
        )

        response = self.client.post(self.url, self.bundle_post_data([row]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice.", count=2)
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_product_create_htmx_previews_candidates_without_saving(self):
        self.seed_preview_vocabulary(self.business)
        self.seed_preview_vocabulary(
            self.other_business,
            product_type_name="Dress",
            product_type_alias="gown",
            tag_name="Private",
            material="Silk",
            size="L",
            color="Red",
        )
        counts_before = (
            Product.objects.count(),
            ProductChoice.objects.count(),
            ProductMaterialFact.objects.count(),
        )
        data = self.bundle_post_data(
            [self.active_choice_row()],
            name="Unsaved preview product",
            description="pants Classic Cotton M Black Dress Private Silk L Red",
        )
        data["intent"] = "preview_recognition"
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            data,
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_recognition_preview.html")
        self.assertNotContains(response, "<form")
        self.assertContains(response, "Recognized candidates")
        self.assertContains(response, "Product type")
        self.assertContains(response, "Trousers")
        self.assertContains(response, "Observed: “pants”")
        self.assertContains(response, "Tag")
        self.assertContains(response, "Material")
        self.assertContains(response, "Choice size")
        self.assertContains(response, "Choice color")
        self.assertContains(response, "Needs confirmation", count=5)
        self.assertContains(response, "Use in choices", count=2)
        self.assertContains(response, "Review as material", count=1)
        self.assertContains(
            response,
            'value="transfer_material_candidate:2:material:14:20:Cotton"',
        )
        self.assertContains(
            response,
            'value="transfer_choice_candidate:3:choice_size:21:22:M"',
        )
        self.assertContains(
            response,
            'value="transfer_choice_candidate:4:choice_color:23:28:Black"',
        )
        self.assertNotContains(
            response,
            'value="transfer_choice_candidate:0:product_type:0:5:Trousers"',
        )
        self.assertFalse(response.context["show_form_errors"])
        self.assertEqual(
            [
                candidate.canonical_value
                for candidate in response.context["recognition_preview"].candidates
            ],
            ["Trousers", "Classic", "Cotton", "M", "Black"],
        )
        self.assertEqual(
            (
                Product.objects.count(),
                ProductChoice.objects.count(),
                ProductMaterialFact.objects.count(),
            ),
            counts_before,
        )
        self.assertFalse(
            Product.objects.filter(name="Unsaved preview product").exists()
        )

    def test_product_create_htmx_transfers_material_without_saving(self):
        self.seed_preview_vocabulary(self.business)
        fact_count = ProductMaterialFact.objects.count()
        data = self.bundle_post_data(
            [self.active_choice_row()],
            name="Unsaved material product",
            description="Cotton",
            material_rows=[{}],
        )
        data["intent"] = self.material_transfer_intent(0, 0, 6, "Cotton")
        self.client.force_login(self.owner)

        response = self.client.post(self.url, data, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_material_section.html")
        transferred_form = response.context["material_formset"].forms[0]
        self.assertEqual(
            transferred_form["canonical_material"].value(),
            "Cotton",
        )
        self.assertEqual(transferred_form["original_text"].value(), "Cotton")
        self.assertEqual(
            transferred_form["source"].value(),
            ProductMaterialFact.Source.DESCRIPTION,
        )
        self.assertEqual(
            response.context["material_transfer_feedback"],
            'Material "Cotton" added to Material 1. Review the fact before saving.',
        )
        self.assertEqual(Product.objects.filter(name="Unsaved material product").count(), 0)
        self.assertEqual(ProductMaterialFact.objects.count(), fact_count)

    def test_product_create_rejects_stale_material_candidate_transfer(self):
        self.seed_preview_vocabulary(self.business)
        data = self.bundle_post_data(
            [self.active_choice_row()],
            description="Cotton",
            material_rows=[{}],
        )
        data["intent"] = self.material_transfer_intent(0, 0, 6, "Silk")
        self.client.force_login(self.owner)

        response = self.client.post(self.url, data, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_material_section.html")
        self.assertContains(response, "That candidate is no longer available")
        self.assertEqual(Product.objects.count(), 1)

    def test_product_create_invalid_material_preserves_input_without_writes(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [self.active_choice_row()],
                material_rows=[self.material_row(percentage="101")],
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Material percentage must be between 1 and 100.",
        )
        self.assertContains(response, 'value="Cotton"')
        self.assertFalse(Product.objects.exists())
        self.assertFalse(ProductChoice.objects.exists())
        self.assertFalse(ProductMaterialFact.objects.exists())

    def test_product_create_htmx_transfers_size_without_saving(self):
        row = self.active_choice_row(
            size="",
            quantity="7",
        )
        data = self.bundle_post_data(
            [row],
            name="Unsaved transfer product",
            description="M Black",
        )
        data["intent"] = self.transfer_intent(
            0,
            SemanticDestination.CHOICE_SIZE,
            0,
            1,
            "M",
        )
        self.client.force_login(self.owner)

        response = self.client.post(self.url, data, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_choice_section.html")
        transferred_form = response.context["choice_formset"].forms[0]
        self.assertEqual(transferred_form["size"].value(), str(self.size.pk))
        self.assertEqual(transferred_form["color"].value(), str(self.color.pk))
        self.assertEqual(transferred_form["quantity"].value(), "7")
        self.assertEqual(
            response.context["choice_transfer_feedback"],
            'Size "M" added to Choice 1. Review the row before saving.',
        )
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_product_create_full_page_transfer_preserves_product_input(self):
        data = self.bundle_post_data(
            [self.active_choice_row(color="")],
            name="Unsaved full-page product",
            description="Black",
        )
        data["next"] = f"{self.list_url}?from=transfer"
        data["intent"] = self.transfer_intent(
            0,
            SemanticDestination.CHOICE_COLOR,
            0,
            5,
            "Black",
        )
        self.client.force_login(self.owner)

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_form.html")
        transferred_form = response.context["choice_formset"].forms[0]
        self.assertEqual(transferred_form["color"].value(), str(self.color.pk))
        self.assertContains(response, 'value="Unsaved full-page product"')
        self.assertContains(response, "Black")
        self.assertEqual(
            response.context["return_url"],
            f"{self.list_url}?from=transfer",
        )
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_product_create_transfers_aliases_to_one_canonical_choice_row(self):
        BusinessSizeAlias.objects.create(
            business=self.business,
            size=self.size,
            alias="M-ზომა",
        )
        BusinessColorAlias.objects.create(
            business=self.business,
            color=self.color,
            alias="შავი",
        )
        data = self.bundle_post_data(
            [self.active_choice_row(size="", color="", quantity="0")],
            name="Unsaved alias product",
            description="M-ზომა შავი",
        )
        data["intent"] = self.transfer_intent(
            0,
            SemanticDestination.CHOICE_SIZE,
            0,
            6,
            "M",
        )
        self.client.force_login(self.owner)

        size_response = self.client.post(
            self.url,
            data,
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(size_response.status_code, 200)
        self.assertContains(size_response, "This field is required.")
        next_data = size_response.context["choice_formset"].data.copy()
        next_data["intent"] = self.transfer_intent(
            1,
            SemanticDestination.CHOICE_COLOR,
            7,
            11,
            "Black",
        )

        color_response = self.client.post(
            self.url,
            next_data,
            HTTP_HX_REQUEST="true",
        )

        transferred_form = color_response.context["choice_formset"].forms[0]
        self.assertEqual(transferred_form["size"].value(), str(self.size.pk))
        self.assertEqual(transferred_form["color"].value(), str(self.color.pk))
        self.assertEqual(
            color_response.context["choice_transfer_feedback"],
            'Color "Black" added to Choice 1. Review the row before saving.',
        )
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_product_create_transfer_appends_row_without_merging_duplicates(self):
        data = self.bundle_post_data(
            [self.active_choice_row(quantity="5")],
            name="Unsaved duplicate product",
            description="M",
        )
        data["intent"] = self.transfer_intent(
            0,
            SemanticDestination.CHOICE_SIZE,
            0,
            1,
            "M",
        )
        self.client.force_login(self.owner)

        response = self.client.post(self.url, data, HTTP_HX_REQUEST="true")

        formset = response.context["choice_formset"]
        self.assertEqual(formset.total_form_count(), 2)
        self.assertEqual(formset.forms[0]["size"].value(), str(self.size.pk))
        self.assertEqual(formset.forms[0]["quantity"].value(), "5")
        self.assertEqual(formset.forms[1]["size"].value(), str(self.size.pk))
        self.assertEqual(formset.forms[1]["color"].value(), "")
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_product_create_rejects_non_choice_candidate_transfer(self):
        BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        data = self.bundle_post_data(
            [self.active_choice_row()],
            name="Unsaved product",
            description="Trousers",
        )
        data["intent"] = self.transfer_intent(
            0,
            SemanticDestination.PRODUCT_TYPE,
            0,
            8,
            "Trousers",
        )
        self.client.force_login(self.owner)

        response = self.client.post(self.url, data, HTTP_HX_REQUEST="true")

        self.assertContains(
            response,
            "Only Size and Color candidates can become choices.",
        )
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_product_create_rejects_cross_business_or_stale_candidate_transfer(self):
        data = self.bundle_post_data(
            [self.active_choice_row(size="")],
            name="Unsaved product",
            description="L Red",
        )
        data["intent"] = self.transfer_intent(
            0,
            SemanticDestination.CHOICE_SIZE,
            0,
            1,
            "L",
        )
        self.client.force_login(self.owner)

        response = self.client.post(self.url, data, HTTP_HX_REQUEST="true")

        self.assertContains(response, "That candidate is no longer available.")
        transferred_form = response.context["choice_formset"].forms[0]
        self.assertEqual(transferred_form["size"].value(), "")
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_product_create_rejects_candidate_when_preview_identity_has_shifted(self):
        data = self.bundle_post_data(
            [self.active_choice_row(size="")],
            name="Unsaved product",
            description="M Black",
        )
        data["intent"] = self.transfer_intent(
            0,
            SemanticDestination.CHOICE_SIZE,
            0,
            1,
            "M",
        )
        self.size.is_active = False
        self.size.save(update_fields=["is_active"])
        self.client.force_login(self.owner)

        response = self.client.post(self.url, data, HTTP_HX_REQUEST="true")

        self.assertContains(response, "That candidate is no longer available.")
        transferred_form = response.context["choice_formset"].forms[0]
        self.assertEqual(transferred_form["size"].value(), "")
        self.assertEqual(transferred_form["color"].value(), str(self.color.pk))
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_product_create_rejects_candidate_when_canonical_meaning_has_changed(self):
        data = self.bundle_post_data(
            [self.active_choice_row(size="")],
            name="Unsaved product",
            description="M",
        )
        data["intent"] = self.transfer_intent(
            0,
            SemanticDestination.CHOICE_SIZE,
            0,
            1,
            "M",
        )
        self.size.name = "Medium"
        self.size.save()
        BusinessSizeAlias.objects.create(
            business=self.business,
            size=self.size,
            alias="M",
        )
        self.client.force_login(self.owner)

        response = self.client.post(self.url, data, HTTP_HX_REQUEST="true")

        self.assertContains(response, "That candidate is no longer available.")
        transferred_form = response.context["choice_formset"].forms[0]
        self.assertEqual(transferred_form["size"].value(), "")
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_product_create_htmx_preview_does_not_require_a_valid_bundle(self):
        self.seed_preview_vocabulary(self.business)
        data = self.bundle_post_data(
            [{}],
            name="",
            description="pants",
        )
        data["intent"] = "preview_recognition"
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            data,
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_recognition_preview.html")
        self.assertContains(response, "Trousers")
        self.assertNotContains(response, "This field is required.")
        self.assertNotContains(
            response,
            "An active product requires at least one active choice.",
        )
        self.assertEqual(Product.objects.count(), 1)

    def test_product_create_validation_error_preserves_recognition_preview(self):
        self.seed_preview_vocabulary(self.business)
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [self.active_choice_row()],
                name="",
                description="pants Classic",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, "Recognized candidates")
        self.assertContains(response, "Trousers")
        self.assertContains(response, "Classic")
        self.assertTrue(response.context["show_form_errors"])
        self.assertEqual(Product.objects.count(), 1)

    def test_product_create_htmx_preview_does_not_leak_other_business_vocabulary(self):
        self.seed_preview_vocabulary(
            self.other_business,
            product_type_name="Dress",
            product_type_alias="gown",
            tag_name="Private",
            material="Silk",
            size="L",
            color="Red",
        )
        data = self.bundle_post_data(
            [{}],
            lifecycle=Product.Lifecycle.DRAFT,
            description="gown Private Silk L Red",
        )
        data["intent"] = "preview_recognition"
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            data,
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_recognition_preview.html")
        self.assertContains(response, "No known candidates found for this Business.")
        self.assertEqual(response.context["recognition_preview"].candidates, ())

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

        data = self.bundle_post_data([self.active_choice_row()])
        data.update(
            {
                "business": self.other_business.pk,
                "choices-0-business": self.other_business.pk,
            }
        )

        response = self.client.post(
            self.url,
            data,
        )

        self.assertRedirects(response, self.list_url)
        product = Product.objects.get()
        self.assertEqual(product.business, self.business)
        self.assertEqual(product.name, "Black trousers")
        self.assertEqual(product.description, "Classic black trousers.")
        self.assertEqual(product.lifecycle, Product.Lifecycle.ACTIVE)
        choice = ProductChoice.objects.get()
        self.assertEqual(choice.business, self.business)
        self.assertEqual(choice.product, product)
        self.assertEqual(choice.size, self.size)
        self.assertEqual(choice.color, self.color)
        self.assertEqual(choice.quantity, 2)

    def test_product_create_active_requires_an_active_choice(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data([{}], name="Preserved trousers"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "An active product requires at least one active choice.",
        )
        self.assertContains(response, 'value="Preserved trousers"')
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_product_create_preserves_choice_errors_and_input_atomically(self):
        self.client.force_login(self.owner)
        invalid_choice = self.active_choice_row(color="")

        response = self.client.post(
            self.url,
            self.bundle_post_data([invalid_choice]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, f'value="{self.size.pk}" selected')
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(ProductChoice.objects.count(), 0)

    def test_product_create_draft_allows_empty_choice_row(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data([{}], lifecycle=Product.Lifecycle.DRAFT),
        )

        self.assertRedirects(response, self.list_url)
        product = Product.objects.get()
        self.assertEqual(product.lifecycle, Product.Lifecycle.DRAFT)
        self.assertFalse(product.choices.exists())

    def test_product_create_preserves_validation_errors_without_creating_product(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [self.active_choice_row()],
                name="",
                description="",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_form.html")
        self.assertContains(response, "This field is required.")
        self.assertEqual(Product.objects.count(), 0)

    def test_product_create_rejects_external_next_url(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            f"{self.url}?next=https://example.com/escape",
            self.bundle_post_data([self.active_choice_row()]),
        )

        self.assertRedirects(response, self.list_url)
        self.assertNotIn("example.com", response["Location"])


class ProductUpdateViewTests(ProductBundleViewTestMixin, TestCase):
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
        self.size = size_value(self.business, "M")
        self.large_size = size_value(self.business, "L")
        self.extra_large_size = size_value(self.business, "XL")
        self.color = color_value(self.business, "Black")
        self.navy = color_value(self.business, "Navy")
        self.other_size = size_value(self.other_business, "L")
        self.other_color = color_value(self.other_business, "Private red")
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
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        tag = BusinessTag.objects.create(
            business=self.business,
            name="Classic",
        )
        BusinessProductType.objects.create(
            business=self.other_business,
            name="PRIVATE-OTHER-TYPE",
        )
        BusinessTag.objects.create(
            business=self.other_business,
            name="PRIVATE-OTHER-TAG",
        )
        self.product.product_type = product_type
        self.product.save(update_fields=["product_type"])
        ProductTag.objects.create(
            business=self.business,
            product=self.product,
            tag=tag,
        )
        owned_choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=2,
        )
        owned_material = ProductMaterialFact.objects.create(
            business=self.business,
            product=self.product,
            canonical_material="Cotton",
            percentage=70,
            original_text="70% cotton",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )
        ProductChoice.objects.create(
            business=self.other_business,
            product=self.other_product,
            size=self.other_size,
            color=self.other_color,
            quantity=8,
        )
        ProductMaterialFact.objects.create(
            business=self.other_business,
            product=self.other_product,
            canonical_material="PRIVATE-OTHER-MATERIAL",
            original_text="PRIVATE-OTHER-MATERIAL",
            source=ProductMaterialFact.Source.MANUAL,
        )
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_form.html")
        self.assertContains(response, "Edit Black trousers")
        self.assertContains(response, 'value="Black trousers"')
        self.assertContains(response, "Classic black trousers.")
        self.assertEqual(
            response.context["form"]["product_type"].value(),
            product_type.pk,
        )
        self.assertEqual(response.context["form"]["tags"].value(), [tag.pk])
        self.assertNotContains(response, "PRIVATE-OTHER-TYPE")
        self.assertNotContains(response, "PRIVATE-OTHER-TAG")
        self.assertContains(response, 'name="choices-TOTAL_FORMS"')
        self.assertContains(response, f'value="{owned_choice.pk}"')
        self.assertContains(response, 'name="materials-TOTAL_FORMS"')
        self.assertContains(response, f'value="{owned_material.pk}"')
        self.assertContains(response, 'value="Cotton"')
        self.assertContains(response, 'value="70"')
        self.assertContains(response, 'value="70% cotton"')
        self.assertNotContains(response, "PRIVATE-OTHER-MATERIAL")
        self.assertContains(response, ">Black</option>")
        self.assertNotContains(response, "Private red")
        self.assertContains(response, "Save changes")
        self.assertNotContains(response, 'name="business"')

    def test_product_edit_replaces_type_and_tags_atomically(self):
        old_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        new_type = BusinessProductType.objects.create(
            business=self.business,
            name="Shirt",
        )
        old_tag = BusinessTag.objects.create(
            business=self.business,
            name="Classic",
        )
        new_tag = BusinessTag.objects.create(
            business=self.business,
            name="Pockets",
        )
        self.product.product_type = old_type
        self.product.save(update_fields=["product_type"])
        ProductTag.objects.create(
            business=self.business,
            product=self.product,
            tag=old_tag,
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [{}],
                lifecycle=Product.Lifecycle.DRAFT,
                product_type=new_type.pk,
                tags=(new_tag.pk,),
            ),
        )

        self.assertRedirects(response, self.list_url)
        self.product.refresh_from_db()
        self.assertEqual(self.product.product_type, new_type)
        self.assertEqual(list(self.product.tags.all()), [new_tag])
        self.assertFalse(
            ProductTag.objects.filter(product=self.product, tag=old_tag).exists()
        )

    def test_product_edit_can_remove_type_and_all_tags(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        tag = BusinessTag.objects.create(
            business=self.business,
            name="Classic",
        )
        self.product.product_type = product_type
        self.product.save(update_fields=["product_type"])
        ProductTag.objects.create(
            business=self.business,
            product=self.product,
            tag=tag,
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [{}],
                lifecycle=Product.Lifecycle.DRAFT,
            ),
        )

        self.assertRedirects(response, self.list_url)
        self.product.refresh_from_db()
        self.assertIsNone(self.product.product_type)
        self.assertFalse(self.product.tags.exists())

    def test_product_edit_corrects_and_removes_confirmed_materials(self):
        corrected_fact = ProductMaterialFact.objects.create(
            business=self.business,
            product=self.product,
            canonical_material="Cottn",
            original_text="cottn",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )
        removed_fact = ProductMaterialFact.objects.create(
            business=self.business,
            product=self.product,
            canonical_material="Silk",
            original_text="silk",
            source=ProductMaterialFact.Source.MANUAL,
        )
        material_rows = [
            self.material_row(
                id=str(corrected_fact.pk),
                canonical_material="Cotton",
                percentage="80",
                original_text="80% cotton",
            ),
            self.material_row(
                id=str(removed_fact.pk),
                canonical_material="Silk",
                percentage="",
                original_text="silk",
                source=ProductMaterialFact.Source.MANUAL,
                DELETE="on",
            ),
        ]
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [{}],
                lifecycle=Product.Lifecycle.DRAFT,
                material_rows=material_rows,
                material_initial_forms=2,
            ),
        )

        self.assertRedirects(response, self.list_url)
        corrected_fact.refresh_from_db()
        self.assertEqual(corrected_fact.canonical_material, "Cotton")
        self.assertEqual(corrected_fact.percentage, 80)
        self.assertFalse(
            ProductMaterialFact.objects.filter(pk=removed_fact.pk).exists()
        )

    def test_product_edit_rejects_another_business_material_id(self):
        owned_fact = ProductMaterialFact.objects.create(
            business=self.business,
            product=self.product,
            canonical_material="Cotton",
            original_text="Cotton",
            source=ProductMaterialFact.Source.MANUAL,
        )
        other_fact = ProductMaterialFact.objects.create(
            business=self.other_business,
            product=self.other_product,
            canonical_material="Silk",
            original_text="Silk",
            source=ProductMaterialFact.Source.MANUAL,
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [{}],
                lifecycle=Product.Lifecycle.DRAFT,
                material_rows=[
                    self.material_row(
                        id=str(other_fact.pk),
                        canonical_material="Leaked",
                    )
                ],
                material_initial_forms=1,
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice.")
        owned_fact.refresh_from_db()
        other_fact.refresh_from_db()
        self.assertEqual(owned_fact.canonical_material, "Cotton")
        self.assertEqual(other_fact.canonical_material, "Silk")

    def test_product_edit_get_previews_saved_description(self):
        self.seed_preview_vocabulary(self.business)
        self.product.description = "pants Classic Cotton M Black"
        self.product.save(update_fields=["description"])
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recognized candidates")
        self.assertContains(response, "Needs confirmation", count=5)
        self.assertEqual(
            len(response.context["recognition_preview"].candidates),
            5,
        )

    def test_product_edit_htmx_adds_color_without_mutating_product(self):
        data = self.bundle_post_data(
            [self.active_choice_row()],
            name="Unsaved product name",
            description="Unsaved description.",
        )
        data.update(
            {
                "intent": "add_color_vocabulary",
                "color-vocabulary-name": "Blue",
                "color-vocabulary-aliases": "ლურჯი, blue color",
            }
        )
        self.client.force_login(self.owner)

        response = self.client.post(self.url, data, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_choice_section.html")
        color = BusinessColor.objects.get(business=self.business, name="Blue")
        self.assertEqual(
            list(color.aliases.values_list("alias", flat=True)),
            ["blue color", "ლურჯი"],
        )
        self.assertEqual(
            response.context["vocabulary_feedback"],
            'Color "Blue" saved.',
        )
        self.assertContains(response, ">Blue</option>")
        self.assertContains(response, f'value="{self.color.pk}" selected')
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Black trousers")
        self.assertEqual(self.product.description, "Classic black trousers.")
        self.assertFalse(self.product.choices.exists())

    def test_product_edit_htmx_preview_does_not_mutate_product(self):
        self.seed_preview_vocabulary(self.business)
        data = self.bundle_post_data(
            [
                self.active_choice_row(
                    size=str(self.extra_large_size.pk),
                    color=str(self.navy.pk),
                    quantity="9",
                )
            ],
            name="Unsaved product name",
            description="pants Cotton M Black",
        )
        data["intent"] = "preview_recognition"
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            data,
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_recognition_preview.html")
        self.assertContains(response, "Recognized candidates")
        self.assertNotContains(response, "<form")
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Black trousers")
        self.assertEqual(self.product.description, "Classic black trousers.")
        self.assertFalse(self.product.choices.exists())

    def test_product_edit_htmx_transfer_preserves_row_and_does_not_mutate(self):
        choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=2,
        )
        row = self.active_choice_row(
            id=str(choice.pk),
            color="",
            quantity="9",
        )
        data = self.bundle_post_data(
            [row],
            initial_forms=1,
            name="Unsaved edit name",
            description="Navy",
        )
        data["next"] = f"{self.list_url}?from=transfer"
        data["intent"] = self.transfer_intent(
            0,
            SemanticDestination.CHOICE_COLOR,
            0,
            4,
            "Navy",
        )
        self.client.force_login(self.owner)

        response = self.client.post(self.url, data, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_choice_section.html")
        transferred_form = response.context["choice_formset"].forms[0]
        self.assertEqual(transferred_form["id"].value(), str(choice.pk))
        self.assertEqual(transferred_form["size"].value(), str(self.size.pk))
        self.assertEqual(transferred_form["color"].value(), str(self.navy.pk))
        self.assertEqual(transferred_form["quantity"].value(), "9")
        self.assertEqual(
            response.context["return_url"],
            f"{self.list_url}?from=transfer",
        )
        self.product.refresh_from_db()
        choice.refresh_from_db()
        self.assertEqual(self.product.name, "Black trousers")
        self.assertEqual(self.product.description, "Classic black trousers.")
        self.assertEqual(choice.color, self.color)
        self.assertEqual(choice.quantity, 2)

    def test_product_edit_updates_owned_product(self):
        self.client.force_login(self.owner)
        return_url = f"{self.list_url}?from=edit"

        data = self.bundle_post_data(
            [self.active_choice_row(size=str(self.large_size.pk), quantity="5")],
            name="Updated trousers",
            description="Updated description.",
        )
        data["next"] = return_url

        response = self.client.post(
            self.url,
            data,
        )

        self.assertRedirects(response, return_url)
        self.product.refresh_from_db()
        self.assertEqual(self.product.business, self.business)
        self.assertEqual(self.product.name, "Updated trousers")
        self.assertEqual(self.product.description, "Updated description.")
        self.assertEqual(self.product.lifecycle, Product.Lifecycle.ACTIVE)
        choice = self.product.choices.get()
        self.assertEqual(choice.business, self.business)
        self.assertEqual(choice.size, self.large_size)
        self.assertEqual(choice.quantity, 5)

    def test_product_edit_updates_and_deactivates_existing_choice(self):
        choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=2,
        )
        row = {
            "id": str(choice.pk),
            "size": str(self.extra_large_size.pk),
            "color": str(self.navy.pk),
            "quantity": "7",
        }
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [row],
                lifecycle=Product.Lifecycle.DRAFT,
                initial_forms=1,
                name="Updated trousers",
            ),
        )

        self.assertRedirects(response, self.list_url)
        choice.refresh_from_db()
        self.assertEqual(choice.business, self.business)
        self.assertEqual(choice.product, self.product)
        self.assertEqual(choice.size, self.extra_large_size)
        self.assertEqual(choice.color, self.navy)
        self.assertEqual(choice.quantity, 7)
        self.assertFalse(choice.is_active)

    def test_product_edit_active_cannot_remove_last_active_choice(self):
        self.product.lifecycle = Product.Lifecycle.ACTIVE
        self.product.save(update_fields=["lifecycle"])
        choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=2,
        )
        row = self.active_choice_row(
            id=str(choice.pk),
            DELETE="on",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [row],
                initial_forms=1,
                name="Must not save",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "An active product requires at least one active choice.",
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Black trousers")
        self.assertTrue(ProductChoice.objects.filter(pk=choice.pk).exists())

    def test_product_edit_draft_can_remove_all_choices(self):
        choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=2,
        )
        row = self.active_choice_row(
            id=str(choice.pk),
            DELETE="on",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [row],
                lifecycle=Product.Lifecycle.DRAFT,
                initial_forms=1,
            ),
        )

        self.assertRedirects(response, self.list_url)
        self.assertFalse(ProductChoice.objects.filter(pk=choice.pk).exists())

    def test_product_edit_rejects_another_business_choice_id(self):
        owned_choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=2,
        )
        other_choice = ProductChoice.objects.create(
            business=self.other_business,
            product=self.other_product,
            size=self.other_size,
            color=self.other_color,
            quantity=4,
        )
        forged_row = self.active_choice_row(
            id=str(other_choice.pk),
            quantity="99",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [forged_row],
                lifecycle=Product.Lifecycle.DRAFT,
                initial_forms=1,
                name="Must not save",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice.")
        self.product.refresh_from_db()
        owned_choice.refresh_from_db()
        other_choice.refresh_from_db()
        self.assertEqual(self.product.name, "Black trousers")
        self.assertEqual(owned_choice.quantity, 2)
        self.assertEqual(other_choice.quantity, 4)

    def test_product_edit_preserves_validation_errors_without_changing_product(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.bundle_post_data(
                [self.active_choice_row()],
                lifecycle="archived",
                name="",
                description="",
            ),
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
