from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

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
