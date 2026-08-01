from dataclasses import FrozenInstanceError

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from businesses.models import Business
from catalog.forms import ProductForm
from catalog.models import BusinessProductType, Product
from catalog.recognition import (
    RecognitionTerm,
    SemanticDestination,
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
