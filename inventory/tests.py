from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from businesses.models import Business
from catalog.models import (
    BusinessColor,
    BusinessSize,
    Product,
    ProductChoice,
)
from inventory.availability import compute_product_availability


class ProductAvailabilityTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="availability-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="availability-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Availability Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Availability Studio",
        )
        self.size = BusinessSize.objects.create(
            business=self.business,
            name="M",
        )
        self.color = BusinessColor.objects.create(
            business=self.business,
            name="Black",
        )
        self.other_size = BusinessSize.objects.create(
            business=self.other_business,
            name="M",
        )
        self.other_color = BusinessColor.objects.create(
            business=self.other_business,
            name="Black",
        )

    def create_product(self, *, business=None, lifecycle=Product.Lifecycle.ACTIVE):
        business = business or self.business
        return Product.objects.create(
            business=business,
            name=f"{business.name} product",
            description="Availability test product.",
            lifecycle=lifecycle,
        )

    def create_choice(
        self,
        *,
        product,
        business=None,
        quantity=1,
        is_active=True,
    ):
        business = business or self.business
        size = self.size if business == self.business else self.other_size
        color = self.color if business == self.business else self.other_color
        return ProductChoice.objects.create(
            business=business,
            product=product,
            size=size,
            color=color,
            quantity=quantity,
            is_active=is_active,
        )

    def test_active_product_with_positive_active_choice_is_available(self):
        product = self.create_product()
        self.create_choice(product=product, quantity=1)

        self.assertTrue(
            compute_product_availability(
                business=self.business,
                product=product,
            )
        )

    def test_draft_product_with_positive_active_choice_is_unavailable(self):
        product = self.create_product(lifecycle=Product.Lifecycle.DRAFT)
        self.create_choice(product=product, quantity=4)

        self.assertFalse(
            compute_product_availability(
                business=self.business,
                product=product,
            )
        )

    def test_active_product_without_positive_active_choice_is_unavailable(self):
        no_choice_product = self.create_product()
        zero_stock_product = self.create_product()
        inactive_stock_product = self.create_product()
        self.create_choice(product=zero_stock_product, quantity=0)
        self.create_choice(
            product=inactive_stock_product,
            quantity=5,
            is_active=False,
        )

        for product in (
            no_choice_product,
            zero_stock_product,
            inactive_stock_product,
        ):
            with self.subTest(product=product.name):
                self.assertFalse(
                    compute_product_availability(
                        business=self.business,
                        product=product,
                    )
                )

    def test_stock_on_another_product_does_not_affect_availability(self):
        owned_product = self.create_product()
        other_product = self.create_product()
        self.create_choice(product=other_product, quantity=7)

        self.assertFalse(
            compute_product_availability(
                business=self.business,
                product=owned_product,
            )
        )

    def test_cross_business_product_is_rejected(self):
        other_product = self.create_product(business=self.other_business)
        self.create_choice(
            business=self.other_business,
            product=other_product,
            quantity=3,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Product must belong to the active Business.",
        ):
            compute_product_availability(
                business=self.business,
                product=other_product,
            )

    def test_availability_computation_does_not_write(self):
        product = self.create_product()
        choice = self.create_choice(product=product, quantity=2)
        product_snapshot = (product.lifecycle, product.updated_at)
        choice_snapshot = (choice.quantity, choice.is_active, choice.updated_at)

        self.assertTrue(
            compute_product_availability(
                business=self.business,
                product=product,
            )
        )

        product.refresh_from_db()
        choice.refresh_from_db()
        self.assertEqual((product.lifecycle, product.updated_at), product_snapshot)
        self.assertEqual(
            (choice.quantity, choice.is_active, choice.updated_at),
            choice_snapshot,
        )
