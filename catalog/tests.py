from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse

from businesses.models import Business
from catalog.forms import ProductForm
from catalog.models import Product


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
