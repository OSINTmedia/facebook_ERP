from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from businesses.models import Business
from catalog.models import (
    BusinessColor,
    BusinessSize,
    Product,
    ProductChoice,
)
from inventory.availability import compute_product_availability
from inventory.models import InventoryAdjustment


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


class InventoryAdjustmentTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="ledger-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="ledger-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Ledger Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Ledger Studio",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="Ledger trousers",
            description="Ledger test product.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        self.other_product = Product.objects.create(
            business=self.other_business,
            name="Other ledger trousers",
            description="Other ledger test product.",
            lifecycle=Product.Lifecycle.ACTIVE,
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
        self.choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=3,
        )
        self.other_choice = ProductChoice.objects.create(
            business=self.other_business,
            product=self.other_product,
            size=self.other_size,
            color=self.other_color,
            quantity=8,
        )

    def create_adjustment(self, **overrides):
        values = {
            "business": self.business,
            "choice": self.choice,
            "actor": self.owner,
            "quantity_before": 3,
            "quantity_after": 2,
            "delta": -1,
        }
        values.update(overrides)
        return InventoryAdjustment.objects.create(**values)

    def test_owned_adjustment_records_transition_without_changing_stock(self):
        choice_snapshot = (
            self.choice.quantity,
            self.choice.is_active,
            self.choice.updated_at,
        )

        adjustment = self.create_adjustment()

        self.choice.refresh_from_db()
        self.assertEqual(adjustment.business, self.business)
        self.assertEqual(adjustment.choice, self.choice)
        self.assertEqual(adjustment.actor, self.owner)
        self.assertEqual(adjustment.quantity_before, 3)
        self.assertEqual(adjustment.quantity_after, 2)
        self.assertEqual(adjustment.delta, -1)
        self.assertIsNotNone(adjustment.created_at)
        self.assertEqual(
            (
                self.choice.quantity,
                self.choice.is_active,
                self.choice.updated_at,
            ),
            choice_snapshot,
        )

    def test_adjustment_targets_one_distinct_choice_row(self):
        duplicate_choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=3,
        )

        adjustment = self.create_adjustment()

        self.assertEqual(list(self.choice.inventory_adjustments.all()), [adjustment])
        self.assertFalse(duplicate_choice.inventory_adjustments.exists())

    def test_cross_business_choice_is_rejected(self):
        adjustment = InventoryAdjustment(
            business=self.business,
            choice=self.other_choice,
            actor=self.owner,
            quantity_before=8,
            quantity_after=7,
            delta=-1,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Choice must belong to the active Business.",
        ):
            adjustment.full_clean()
        with self.assertRaisesMessage(
            ValidationError,
            "Choice must belong to the active Business.",
        ):
            adjustment.save()

    def test_actor_must_own_business(self):
        adjustment = InventoryAdjustment(
            business=self.business,
            choice=self.choice,
            actor=self.other_owner,
            quantity_before=3,
            quantity_after=4,
            delta=1,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Actor must own the active Business.",
        ):
            adjustment.full_clean()
        with self.assertRaisesMessage(
            ValidationError,
            "Actor must own the active Business.",
        ):
            adjustment.save()

    def test_negative_quantities_zero_delta_and_inconsistent_math_are_rejected(self):
        invalid_values = (
            ({"quantity_before": -1, "quantity_after": 0, "delta": 1}, "Starting"),
            ({"quantity_after": -1, "delta": -4}, "Resulting"),
            ({"quantity_after": 3, "delta": 0}, "cannot be zero"),
            ({"quantity_after": 1, "delta": -1}, "must be consistent"),
        )

        for overrides, message in invalid_values:
            with self.subTest(overrides=overrides):
                adjustment = InventoryAdjustment(
                    business=self.business,
                    choice=self.choice,
                    actor=self.owner,
                    quantity_before=3,
                    quantity_after=2,
                    delta=-1,
                )
                for field_name, value in overrides.items():
                    setattr(adjustment, field_name, value)

                with self.assertRaisesMessage(ValidationError, message):
                    adjustment.save()

    def test_database_rejects_invalid_transition_when_model_save_is_bypassed(self):
        invalid_values = (
            {"quantity_before": -1, "quantity_after": 0, "delta": 1},
            {"quantity_before": 3, "quantity_after": -1, "delta": -4},
            {"quantity_before": 3, "quantity_after": 3, "delta": 0},
            {"quantity_before": 3, "quantity_after": 1, "delta": -1},
        )

        for values in invalid_values:
            with self.subTest(values=values):
                invalid_adjustment = InventoryAdjustment(
                    business=self.business,
                    choice=self.choice,
                    actor=self.owner,
                    **values,
                )

                with self.assertRaises(IntegrityError):
                    with transaction.atomic():
                        InventoryAdjustment.objects.bulk_create([invalid_adjustment])

    def test_adjustment_cannot_be_changed_or_deleted_through_model_api(self):
        adjustment = self.create_adjustment()
        adjustment.quantity_after = 1
        adjustment.delta = -2

        with self.assertRaisesMessage(
            ValidationError,
            "Inventory adjustments cannot be changed.",
        ):
            adjustment.save()
        with self.assertRaisesMessage(
            ValidationError,
            "Inventory adjustments cannot be changed.",
        ):
            InventoryAdjustment.objects.filter(pk=adjustment.pk).update(delta=-2)
        with self.assertRaisesMessage(
            ValidationError,
            "Inventory adjustments cannot be deleted.",
        ):
            adjustment.delete()
        with self.assertRaisesMessage(
            ValidationError,
            "Inventory adjustments cannot be deleted.",
        ):
            InventoryAdjustment.objects.filter(pk=adjustment.pk).delete()

        adjustment.refresh_from_db()
        self.assertEqual(adjustment.quantity_after, 2)
        self.assertEqual(adjustment.delta, -1)

    def test_adjustment_protects_business_choice_and_actor_history(self):
        self.create_adjustment()

        for protected_object in (self.business, self.choice, self.owner):
            with self.subTest(protected_object=protected_object):
                with self.assertRaises(ProtectedError):
                    protected_object.delete()
