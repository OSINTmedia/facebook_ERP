from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.db.models.deletion import ProtectedError
from django.test import TestCase, TransactionTestCase

from businesses.models import Business
from catalog.models import (
    BusinessColor,
    BusinessSize,
    Product,
    ProductChoice,
)
from inventory.availability import compute_product_availability
from inventory.models import InventoryAdjustment
from inventory.mutations import apply_choice_quantity_delta


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


class InventoryMutationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="mutation-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="mutation-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Mutation Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Mutation Studio",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="Mutation trousers",
            description="Mutation test product.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        self.other_product = Product.objects.create(
            business=self.other_business,
            name="Other mutation trousers",
            description="Other mutation test product.",
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
            quantity=0,
        )
        self.other_choice = ProductChoice.objects.create(
            business=self.other_business,
            product=self.other_product,
            size=self.other_size,
            color=self.other_color,
            quantity=5,
        )

    def apply_delta(self, delta, **overrides):
        values = {
            "business": self.business,
            "choice": self.choice,
            "actor": self.owner,
            "delta": delta,
        }
        values.update(overrides)
        return apply_choice_quantity_delta(**values)

    def test_increment_records_adjustment_and_returns_available_transition(self):
        original_state = (self.choice.is_active, self.product.lifecycle)

        result = self.apply_delta(1)

        self.choice.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(self.choice.quantity, 1)
        self.assertEqual(
            (self.choice.is_active, self.product.lifecycle),
            original_state,
        )
        self.assertEqual(result.choice.pk, self.choice.pk)
        self.assertEqual(result.choice.quantity, 1)
        self.assertTrue(result.is_available)
        self.assertEqual(result.adjustment.business, self.business)
        self.assertEqual(result.adjustment.choice, self.choice)
        self.assertEqual(result.adjustment.actor, self.owner)
        self.assertEqual(result.adjustment.quantity_before, 0)
        self.assertEqual(result.adjustment.quantity_after, 1)
        self.assertEqual(result.adjustment.delta, 1)

    def test_decrement_records_adjustment_and_returns_sold_out_transition(self):
        self.choice.quantity = 1
        self.choice.save(update_fields=["quantity", "updated_at"])

        result = self.apply_delta(-1)

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertFalse(result.is_available)
        self.assertEqual(result.adjustment.quantity_before, 1)
        self.assertEqual(result.adjustment.quantity_after, 0)
        self.assertEqual(result.adjustment.delta, -1)

    def test_other_stock_keeps_product_available_after_target_reaches_zero(self):
        self.choice.quantity = 1
        self.choice.save(update_fields=["quantity", "updated_at"])
        other_choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=2,
        )

        result = self.apply_delta(-1)

        self.choice.refresh_from_db()
        other_choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertEqual(other_choice.quantity, 2)
        self.assertTrue(result.is_available)
        self.assertFalse(other_choice.inventory_adjustments.exists())

    def test_invalid_delta_leaves_choice_and_ledger_unchanged(self):
        for delta in (0, 2, -2, True, 1.0, "1", None):
            with self.subTest(delta=delta):
                with self.assertRaisesMessage(
                    ValidationError,
                    "Quantity delta must be +1 or -1.",
                ):
                    self.apply_delta(delta)

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_unsaved_choice_is_rejected_without_writes(self):
        unsaved_choice = ProductChoice(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=4,
        )

        with self.assertRaisesMessage(
            ValueError,
            "An existing ProductChoice is required.",
        ):
            self.apply_delta(1, choice=unsaved_choice)

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_underflow_leaves_choice_and_ledger_unchanged(self):
        with self.assertRaisesMessage(
            ValidationError,
            "Choice quantity cannot be negative.",
        ):
            self.apply_delta(-1)

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_cross_business_choice_is_rejected_without_writes(self):
        with self.assertRaisesMessage(
            ValidationError,
            "Choice must belong to the active Business.",
        ):
            self.apply_delta(1, choice=self.other_choice)

        self.choice.refresh_from_db()
        self.other_choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertEqual(self.other_choice.quantity, 5)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_wrong_actor_is_rejected_without_writes(self):
        with self.assertRaisesMessage(
            ValidationError,
            "Actor must own the active Business.",
        ):
            self.apply_delta(1, actor=self.other_owner)

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_adjustment_failure_rolls_back_quantity_write(self):
        with patch(
            "inventory.mutations.InventoryAdjustment.objects.create",
            side_effect=IntegrityError("ledger write failed"),
        ):
            with self.assertRaises(IntegrityError):
                self.apply_delta(1)

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertFalse(InventoryAdjustment.objects.exists())


class InventoryMutationConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="mutation-concurrency@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Concurrency Studio",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="Concurrency trousers",
            description="Concurrency test product.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        size = BusinessSize.objects.create(
            business=self.business,
            name="M",
        )
        color = BusinessColor.objects.create(
            business=self.business,
            name="Black",
        )
        self.choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=size,
            color=color,
            quantity=1,
        )

    def test_concurrent_decrements_serialize_without_lost_update(self):
        start = Barrier(2)

        def decrement():
            close_old_connections()
            try:
                business = Business.objects.get(pk=self.business.pk)
                choice = ProductChoice.objects.get(pk=self.choice.pk)
                actor = get_user_model().objects.get(pk=self.owner.pk)
                start.wait(timeout=5)
                try:
                    result = apply_choice_quantity_delta(
                        business=business,
                        choice=choice,
                        actor=actor,
                        delta=-1,
                    )
                    return "applied", result.adjustment.pk
                except ValidationError as error:
                    return "rejected", str(error)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: decrement(), range(2)))

        self.choice.refresh_from_db()
        adjustments = list(InventoryAdjustment.objects.all())
        self.assertCountEqual(
            [result[0] for result in results],
            ["applied", "rejected"],
        )
        self.assertEqual(self.choice.quantity, 0)
        self.assertEqual(len(adjustments), 1)
        self.assertEqual(adjustments[0].quantity_before, 1)
        self.assertEqual(adjustments[0].quantity_after, 0)
        self.assertEqual(adjustments[0].delta, -1)
