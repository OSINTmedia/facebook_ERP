from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.db.models.deletion import ProtectedError
from django.http import QueryDict
from django.test import Client, TestCase, TransactionTestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from businesses.models import Business
from catalog.models import (
    BusinessColor,
    BusinessSize,
    Product,
    ProductChoice,
)
from inventory.availability import (
    compute_availability_from_stock_state,
    compute_product_availability,
)
from inventory.models import InventoryAdjustment
from inventory.mutations import (
    apply_choice_quantity_delta,
    initialize_choice_quantity,
)


def maximum_choice_quantity():
    quantity_field = ProductChoice._meta.get_field("quantity")
    _, maximum = connection.ops.integer_field_range(
        quantity_field.get_internal_type()
    )
    return maximum


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

    def test_shared_stock_state_evaluator_keeps_lifecycle_separate(self):
        self.assertTrue(
            compute_availability_from_stock_state(
                product_lifecycle=Product.Lifecycle.ACTIVE,
                has_positive_active_choice=True,
            )
        )
        self.assertFalse(
            compute_availability_from_stock_state(
                product_lifecycle=Product.Lifecycle.ACTIVE,
                has_positive_active_choice=False,
            )
        )
        self.assertFalse(
            compute_availability_from_stock_state(
                product_lifecycle=Product.Lifecycle.DRAFT,
                has_positive_active_choice=True,
            )
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

    def test_bulk_create_validates_all_business_scopes_before_writing(self):
        invalid_adjustments = (
            (
                InventoryAdjustment(
                    business=self.business,
                    choice=self.other_choice,
                    actor=self.owner,
                    quantity_before=8,
                    quantity_after=7,
                    delta=-1,
                ),
                "Choice must belong to the active Business.",
            ),
            (
                InventoryAdjustment(
                    business=self.business,
                    choice=self.choice,
                    actor=self.other_owner,
                    quantity_before=3,
                    quantity_after=4,
                    delta=1,
                ),
                "Actor must own the active Business.",
            ),
        )

        for invalid_adjustment, message in invalid_adjustments:
            with self.subTest(message=message):
                valid_adjustment = InventoryAdjustment(
                    business=self.business,
                    choice=self.choice,
                    actor=self.owner,
                    quantity_before=3,
                    quantity_after=2,
                    delta=-1,
                )
                with self.assertRaisesMessage(ValidationError, message):
                    InventoryAdjustment.objects.bulk_create(
                        [valid_adjustment, invalid_adjustment]
                    )
                self.assertFalse(InventoryAdjustment.objects.exists())

    def test_bulk_create_preserves_valid_owned_transition_facts(self):
        adjustment = InventoryAdjustment(
            business=self.business,
            choice=self.choice,
            actor=self.owner,
            quantity_before=3,
            quantity_after=2,
            delta=-1,
        )

        created_adjustments = InventoryAdjustment.objects.bulk_create(
            [adjustment]
        )

        self.assertEqual(created_adjustments, [adjustment])
        self.assertIsNotNone(adjustment.pk)
        self.assertEqual(InventoryAdjustment.objects.get(), adjustment)

    def test_bulk_create_rejects_conflict_modes_that_could_hide_or_change_facts(self):
        adjustment = self.create_adjustment()
        replacement = InventoryAdjustment(
            pk=adjustment.pk,
            business=self.business,
            choice=self.choice,
            actor=self.owner,
            quantity_before=3,
            quantity_after=4,
            delta=1,
        )

        conflict_options = (
            {"ignore_conflicts": True},
            {
                "update_conflicts": True,
                "update_fields": ["quantity_after", "delta"],
                "unique_fields": ["pk"],
            },
        )
        for options in conflict_options:
            with self.subTest(options=options):
                with self.assertRaisesMessage(
                    ValidationError,
                    "Inventory adjustment conflict handling is not allowed.",
                ):
                    InventoryAdjustment.objects.bulk_create(
                        [replacement],
                        **options,
                    )

        adjustment.refresh_from_db()
        self.assertEqual(adjustment.quantity_after, 2)
        self.assertEqual(adjustment.delta, -1)
        self.assertEqual(InventoryAdjustment.objects.count(), 1)

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

    def initialize_quantity(self, quantity, **overrides):
        values = {
            "business": self.business,
            "choice": self.choice,
            "actor": self.owner,
            "quantity": quantity,
        }
        values.update(overrides)
        return initialize_choice_quantity(**values)

    def test_initial_quantity_records_one_adjustment_and_returns_availability(self):
        result = self.initialize_quantity(7)

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 7)
        self.assertEqual(result.choice.pk, self.choice.pk)
        self.assertEqual(result.choice.quantity, 7)
        self.assertTrue(result.is_available)
        self.assertEqual(result.adjustment.business, self.business)
        self.assertEqual(result.adjustment.choice, self.choice)
        self.assertEqual(result.adjustment.actor, self.owner)
        self.assertEqual(result.adjustment.quantity_before, 0)
        self.assertEqual(result.adjustment.quantity_after, 7)
        self.assertEqual(result.adjustment.delta, 7)
        self.assertEqual(InventoryAdjustment.objects.count(), 1)

    def test_invalid_initial_quantity_leaves_choice_and_ledger_unchanged(self):
        for quantity in (0, -1, True, 1.0, "1", None):
            with self.subTest(quantity=quantity):
                with self.assertRaisesMessage(
                    ValidationError,
                    "Initial quantity must be a positive integer.",
                ):
                    self.initialize_quantity(quantity)

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_initial_quantity_rejects_storage_overflow_without_writes(self):
        maximum = maximum_choice_quantity()

        with self.assertRaisesMessage(
            ValidationError,
            f"Choice quantity cannot exceed {maximum}.",
        ):
            self.initialize_quantity(maximum + 1)

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_initial_quantity_rejects_unsaved_choice_without_writes(self):
        unsaved_choice = ProductChoice(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=0,
        )

        with self.assertRaisesMessage(
            ValueError,
            "An existing ProductChoice is required.",
        ):
            self.initialize_quantity(3, choice=unsaved_choice)

        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_initial_quantity_rejects_nonzero_choice_without_writes(self):
        self.choice.quantity = 2
        self.choice.save(update_fields=["quantity", "updated_at"])

        with self.assertRaisesMessage(
            ValidationError,
            "Choice quantity must be zero before initialization.",
        ):
            self.initialize_quantity(3)

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 2)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_initial_quantity_rejects_previously_adjusted_choice(self):
        self.apply_delta(1)
        self.apply_delta(-1)

        with self.assertRaisesMessage(
            ValidationError,
            "Choice stock has already been adjusted.",
        ):
            self.initialize_quantity(3)

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertEqual(InventoryAdjustment.objects.count(), 2)

    def test_initial_quantity_rejects_cross_business_choice_and_wrong_actor(self):
        with self.assertRaisesMessage(
            ValidationError,
            "Choice must belong to the active Business.",
        ):
            self.initialize_quantity(3, choice=self.other_choice)

        with self.assertRaisesMessage(
            ValidationError,
            "Actor must own the active Business.",
        ):
            self.initialize_quantity(3, actor=self.other_owner)

        self.choice.refresh_from_db()
        self.other_choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertEqual(self.other_choice.quantity, 5)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_initial_adjustment_failure_rolls_back_quantity_write(self):
        with patch(
            "inventory.mutations.InventoryAdjustment.objects.create",
            side_effect=IntegrityError("ledger write failed"),
        ):
            with self.assertRaises(IntegrityError):
                self.initialize_quantity(4)

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertFalse(InventoryAdjustment.objects.exists())

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

    def test_increment_rejects_storage_overflow_without_writes(self):
        maximum = maximum_choice_quantity()
        self.choice.quantity = maximum
        self.choice.save(update_fields=["quantity", "updated_at"])

        with self.assertRaisesMessage(
            ValidationError,
            f"Choice quantity cannot exceed {maximum}.",
        ):
            self.apply_delta(1)

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, maximum)
        self.assertFalse(InventoryAdjustment.objects.exists())

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


class InventoryMutationRouteTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="route-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="route-other@example.com",
            password="test-password",
        )
        self.owner_without_business = user_model.objects.create_user(
            email="route-no-business@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Route Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Route Studio",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="Route trousers",
            description="Route test product.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        self.other_product = Product.objects.create(
            business=self.other_business,
            name="Other route trousers",
            description="Other route test product.",
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
        other_size = BusinessSize.objects.create(
            business=self.other_business,
            name="M",
        )
        other_color = BusinessColor.objects.create(
            business=self.other_business,
            name="Black",
        )
        self.choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=1,
        )
        self.other_choice = ProductChoice.objects.create(
            business=self.other_business,
            product=self.other_product,
            size=other_size,
            color=other_color,
            quantity=4,
        )
        self.url = reverse(
            "inventory:choice_stock_adjust",
            kwargs={"choice_pk": self.choice.pk},
        )
        self.return_url = f"{reverse('catalog:product_list')}?from=stock"

    def response_messages(self, response):
        return [str(message) for message in get_messages(response.wsgi_request)]

    def test_owner_increment_uses_service_and_safe_return(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {"delta": "1", "next": self.return_url},
        )

        self.assertRedirects(
            response,
            self.return_url,
            fetch_redirect_response=False,
        )
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 2)
        adjustment = InventoryAdjustment.objects.get()
        self.assertEqual(adjustment.business, self.business)
        self.assertEqual(adjustment.choice, self.choice)
        self.assertEqual(adjustment.actor, self.owner)
        self.assertEqual(adjustment.delta, 1)
        self.assertEqual(adjustment.quantity_before, 1)
        self.assertEqual(adjustment.quantity_after, 2)
        self.assertIn("Stock updated to 2.", self.response_messages(response))

    def test_owner_decrement_records_exact_transition(self):
        self.client.force_login(self.owner)

        response = self.client.post(self.url, {"delta": "-1"})

        self.assertRedirects(
            response,
            reverse("catalog:product_list"),
            fetch_redirect_response=False,
        )
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        adjustment = InventoryAdjustment.objects.get()
        self.assertEqual(adjustment.delta, -1)
        self.assertEqual(adjustment.quantity_before, 1)
        self.assertEqual(adjustment.quantity_after, 0)

    def test_htmx_increment_returns_authoritative_choice_controls(self):
        duplicate_choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=5,
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {"delta": "1", "next": self.return_url},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "inventory/_choice_stock_controls.html",
        )
        self.assertContains(
            response,
            f'id="choice-stock-controls-{self.choice.pk}"',
        )
        self.assertNotContains(
            response,
            f'id="choice-stock-controls-{duplicate_choice.pk}"',
        )
        self.assertContains(response, ">2</output>")
        self.assertContains(response, "Stock updated to 2.")
        self.assertContains(response, 'role="status"')
        self.assertContains(response, 'hx-swap="outerHTML"')
        self.choice.refresh_from_db()
        duplicate_choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 2)
        self.assertEqual(duplicate_choice.quantity, 5)
        self.assertEqual(InventoryAdjustment.objects.count(), 1)

    def test_htmx_underflow_returns_controls_with_error_and_no_write(self):
        self.choice.quantity = 0
        self.choice.save(update_fields=["quantity", "updated_at"])
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {"delta": "-1", "next": self.return_url},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "inventory/_choice_stock_controls.html",
        )
        self.assertContains(response, ">0</output>")
        self.assertContains(response, "Choice quantity cannot be negative.")
        self.assertContains(response, 'role="alert"')
        self.assertContains(response, 'name="delta"', count=2)
        self.assertContains(response, 'value="-1"')
        self.assertContains(response, 'value="1"')
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_htmx_increment_at_storage_limit_returns_error_without_write(self):
        maximum = maximum_choice_quantity()
        self.choice.quantity = maximum
        self.choice.save(update_fields=["quantity", "updated_at"])
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {"delta": "1", "next": self.return_url},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "inventory/_choice_stock_controls.html",
        )
        self.assertContains(response, f">{maximum}</output>")
        self.assertContains(
            response,
            f"Choice quantity cannot exceed {maximum}.",
        )
        self.assertContains(response, 'role="alert"')
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, maximum)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_htmx_invalid_delta_returns_current_controls_without_write(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {"delta": "2", "next": self.return_url},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "inventory/_choice_stock_controls.html",
        )
        self.assertContains(response, ">1</output>")
        self.assertContains(response, "Stock adjustment must be +1 or -1.")
        self.assertContains(response, 'role="alert"')
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 1)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_workspace_htmx_increment_returns_complete_authoritative_results(self):
        self.client.force_login(self.owner)
        workspace_url = reverse("catalog:product_list")

        response = self.client.post(
            self.url,
            {
                "delta": "1",
                "next": workspace_url,
                "response_scope": "workspace",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_product_results.html")
        self.assertTemplateUsed(response, "catalog/_product_card.html")
        self.assertTemplateNotUsed(
            response,
            "inventory/_choice_stock_controls.html",
        )
        self.assertContains(response, 'id="product-workspace-results"', count=1)
        self.assertContains(response, "Stock updated to 2.")
        self.assertContains(response, "1 active · 2 total stock")
        self.assertContains(response, ">2</output>")
        self.assertContains(
            response,
            f'data-workspace-focus-choice-id="{self.choice.pk}"',
        )
        self.assertContains(response, 'aria-busy="false"')
        self.assertContains(response, "Refresh results")
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 2)
        self.assertEqual(InventoryAdjustment.objects.count(), 1)

    def test_workspace_htmx_recomputes_availability_filter_membership(self):
        self.client.force_login(self.owner)
        workspace_path = reverse("catalog:product_list")
        available_url = f"{workspace_path}?availability=available"
        sold_out_url = f"{workspace_path}?availability=sold_out"

        sold_out_response = self.client.post(
            self.url,
            {
                "delta": "-1",
                "next": available_url,
                "response_scope": "workspace",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(sold_out_response.status_code, 200)
        self.assertContains(sold_out_response, "<strong>0</strong> products ·")
        self.assertContains(
            sold_out_response,
            "The Product moved out of the current results because its "
            "availability changed.",
        )
        self.assertContains(
            sold_out_response,
            'data-workspace-focus-results="true"',
        )
        self.assertContains(
            sold_out_response,
            "No products match the active filters.",
        )
        self.assertNotContains(sold_out_response, self.product.name)
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)

        available_response = self.client.post(
            self.url,
            {
                "delta": "1",
                "next": sold_out_url,
                "response_scope": "workspace",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(available_response.status_code, 200)
        self.assertContains(available_response, "<strong>0</strong> products ·")
        self.assertContains(
            available_response,
            "The Product moved out of the current results because its "
            "availability changed.",
        )
        self.assertContains(
            available_response,
            "No products match the active filters.",
        )
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 1)
        self.assertEqual(InventoryAdjustment.objects.count(), 2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.lifecycle, Product.Lifecycle.ACTIVE)

    def test_workspace_htmx_underflow_returns_full_results_without_write(self):
        self.choice.quantity = 0
        self.choice.save(update_fields=["quantity", "updated_at"])
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {
                "delta": "-1",
                "next": reverse("catalog:product_list"),
                "response_scope": "workspace",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_product_results.html")
        self.assertContains(response, "Choice quantity cannot be negative.")
        self.assertContains(response, f"Choice #{self.choice.pk}:")
        self.assertContains(response, 'role="alert"')
        self.assertContains(response, "Sold out")
        self.assertContains(response, "1 active · 0 total stock")
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_workspace_htmx_keeps_feedback_when_acted_choice_is_no_longer_visible(self):
        ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=3,
        )
        self.choice.is_active = False
        self.choice.save(update_fields=["is_active", "updated_at"])
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {
                "delta": "1",
                "next": (
                    f'{reverse("catalog:product_list")}'
                    "?availability=available"
                ),
                "response_scope": "workspace",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(
            response,
            f"Choice #{self.choice.pk}: Stock updated to 2.",
        )
        self.assertNotContains(
            response,
            f'data-workspace-focus-choice-id="{self.choice.pk}"',
        )
        self.assertNotContains(
            response,
            "The Product moved out of the current results",
        )
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 2)
        self.assertEqual(InventoryAdjustment.objects.count(), 1)

    def test_malformed_workspace_scope_is_rejected_before_stock_write(self):
        self.client.force_login(self.owner)
        workspace_path = reverse("catalog:product_list")
        invalid_payloads = (
            {
                "delta": "1",
                "next": f"{workspace_path}?unknown=value",
                "response_scope": "workspace",
            },
            {
                "delta": "1",
                "next": "https://example.com/products/",
                "response_scope": "workspace",
            },
            {
                "delta": "1",
                "next": workspace_path,
                "response_scope": "unknown",
            },
        )

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post(
                    self.url,
                    payload,
                    HTTP_HX_REQUEST="true",
                )
                self.assertEqual(response.status_code, 400)

        repeated_scope = QueryDict(mutable=True)
        repeated_scope.update({"delta": "1", "next": workspace_path})
        repeated_scope.setlist("response_scope", ["workspace", "unknown"])
        repeated_response = self.client.post(
            self.url,
            repeated_scope,
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(repeated_response.status_code, 400)
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 1)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_workspace_htmx_response_query_count_is_bounded(self):
        for index in range(8):
            product = Product.objects.create(
                business=self.business,
                name=f"Bounded Product {index}",
                description="Query bound fixture.",
                lifecycle=Product.Lifecycle.ACTIVE,
            )
            ProductChoice.objects.create(
                business=self.business,
                product=product,
                size=self.size,
                color=self.color,
                quantity=1,
            )
        self.client.force_login(self.owner)

        with CaptureQueriesContext(connection) as query_context:
            response = self.client.post(
                self.url,
                {
                    "delta": "1",
                    "next": reverse("catalog:product_list"),
                    "response_scope": "workspace",
                },
                HTTP_HX_REQUEST="true",
            )

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(query_context), 16)

    def test_unauthenticated_post_redirects_to_login_without_writes(self):
        response = self.client.post(self.url, {"delta": "1"})

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.url}",
            fetch_redirect_response=False,
        )
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 1)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_get_is_not_an_allowed_mutation_method(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 1)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_post_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)

        response = csrf_client.post(self.url, {"delta": "1"})

        self.assertEqual(response.status_code, 403)
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 1)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_cross_business_choice_is_not_exposed_or_mutated(self):
        self.client.force_login(self.owner)
        other_url = reverse(
            "inventory:choice_stock_adjust",
            kwargs={"choice_pk": self.other_choice.pk},
        )

        response = self.client.post(other_url, {"delta": "1"})

        self.assertEqual(response.status_code, 404)
        self.choice.refresh_from_db()
        self.other_choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 1)
        self.assertEqual(self.other_choice.quantity, 4)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_workspace_scope_cannot_render_or_mutate_cross_business_choice(self):
        self.client.force_login(self.owner)
        other_url = reverse(
            "inventory:choice_stock_adjust",
            kwargs={"choice_pk": self.other_choice.pk},
        )

        response = self.client.post(
            other_url,
            {
                "delta": "1",
                "next": reverse("catalog:product_list"),
                "response_scope": "workspace",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 404)
        self.choice.refresh_from_db()
        self.other_choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 1)
        self.assertEqual(self.other_choice.quantity, 4)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_invalid_delta_redirects_with_error_without_writes(self):
        self.client.force_login(self.owner)

        for delta in ("", "0", "2", "-2", "1.0", "true"):
            with self.subTest(delta=delta):
                response = self.client.post(
                    self.url,
                    {"delta": delta, "next": self.return_url},
                )
                self.assertRedirects(
                    response,
                    self.return_url,
                    fetch_redirect_response=False,
                )
                self.assertIn(
                    "Stock adjustment must be +1 or -1.",
                    self.response_messages(response),
                )

        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 1)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_underflow_redirects_with_error_without_writes(self):
        self.choice.quantity = 0
        self.choice.save(update_fields=["quantity", "updated_at"])
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {"delta": "-1", "next": self.return_url},
        )

        self.assertRedirects(
            response,
            self.return_url,
            fetch_redirect_response=False,
        )
        self.assertIn(
            "Choice quantity cannot be negative.",
            self.response_messages(response),
        )
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 0)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_external_return_url_falls_back_to_product_list(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {"delta": "1", "next": "https://example.com/escape"},
        )

        self.assertRedirects(
            response,
            reverse("catalog:product_list"),
            fetch_redirect_response=False,
        )
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 2)

    def test_missing_active_business_returns_conflict_without_writes(self):
        self.client.force_login(self.owner_without_business)

        response = self.client.post(self.url, {"delta": "1"})

        self.assertEqual(response.status_code, 409)
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 1)
        self.assertFalse(InventoryAdjustment.objects.exists())

    def test_multiple_businesses_return_conflict_without_writes(self):
        Business.objects.create(owner=self.owner, name="Second Route Studio")
        self.client.force_login(self.owner)

        response = self.client.post(self.url, {"delta": "1"})

        self.assertEqual(response.status_code, 409)
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 1)
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

    def test_concurrent_initializations_allow_one_exact_transition(self):
        self.choice.quantity = 0
        self.choice.save(update_fields=["quantity", "updated_at"])
        start = Barrier(2)

        def initialize(quantity):
            close_old_connections()
            try:
                business = Business.objects.get(pk=self.business.pk)
                choice = ProductChoice.objects.get(pk=self.choice.pk)
                actor = get_user_model().objects.get(pk=self.owner.pk)
                start.wait(timeout=5)
                try:
                    result = initialize_choice_quantity(
                        business=business,
                        choice=choice,
                        actor=actor,
                        quantity=quantity,
                    )
                    return "applied", result.adjustment.pk
                except ValidationError as error:
                    return "rejected", str(error)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(initialize, (5, 7)))

        self.choice.refresh_from_db()
        adjustments = list(InventoryAdjustment.objects.all())
        self.assertCountEqual(
            [result[0] for result in results],
            ["applied", "rejected"],
        )
        self.assertIn(self.choice.quantity, (5, 7))
        self.assertEqual(len(adjustments), 1)
        self.assertEqual(adjustments[0].quantity_before, 0)
        self.assertEqual(adjustments[0].quantity_after, self.choice.quantity)
        self.assertEqual(adjustments[0].delta, self.choice.quantity)

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
