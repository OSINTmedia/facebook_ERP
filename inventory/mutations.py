from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import connection, transaction

from catalog.models import ProductChoice
from inventory.availability import compute_product_availability
from inventory.models import InventoryAdjustment


@dataclass(frozen=True, slots=True)
class ChoiceQuantityDeltaResult:
    choice: ProductChoice
    adjustment: InventoryAdjustment
    is_available: bool


@dataclass(frozen=True, slots=True)
class ChoiceQuantityInitializationResult:
    choice: ProductChoice
    adjustment: InventoryAdjustment
    is_available: bool


def _validate_storable_choice_quantity(quantity):
    """Reject values outside the configured database field range."""
    quantity_field = ProductChoice._meta.get_field("quantity")
    _, maximum = connection.ops.integer_field_range(
        quantity_field.get_internal_type()
    )
    if maximum is not None and quantity > maximum:
        raise ValidationError(f"Choice quantity cannot exceed {maximum}.")


def apply_choice_quantity_delta(*, business, choice, actor, delta):
    """Atomically apply one +1/-1 choice mutation and record its audit fact."""
    if business is None or business.pk is None:
        raise ValueError("An existing Business is required.")
    if choice is None or choice.pk is None:
        raise ValueError("An existing ProductChoice is required.")
    if actor is None or actor.pk is None:
        raise ValueError("An authenticated actor is required.")
    if type(delta) is not int or delta not in (-1, 1):
        raise ValidationError("Quantity delta must be +1 or -1.")
    if choice.business_id != business.pk:
        raise ValidationError("Choice must belong to the active Business.")
    if business.owner_id != actor.pk:
        raise ValidationError("Actor must own the active Business.")

    with transaction.atomic():
        try:
            locked_choice = (
                ProductChoice.objects.select_for_update()
                .select_related("product")
                .get(pk=choice.pk, business=business)
            )
        except ProductChoice.DoesNotExist as error:
            raise ValidationError(
                "Choice must belong to the active Business."
            ) from error

        quantity_before = locked_choice.quantity
        quantity_after = quantity_before + delta
        if quantity_after < 0:
            raise ValidationError("Choice quantity cannot be negative.")
        _validate_storable_choice_quantity(quantity_after)

        locked_choice.quantity = quantity_after
        locked_choice.save(update_fields=["quantity", "updated_at"])
        adjustment = InventoryAdjustment.objects.create(
            business=business,
            choice=locked_choice,
            actor=actor,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            delta=delta,
        )
        is_available = compute_product_availability(
            business=business,
            product=locked_choice.product,
        )

    return ChoiceQuantityDeltaResult(
        choice=locked_choice,
        adjustment=adjustment,
        is_available=is_available,
    )


def initialize_choice_quantity(*, business, choice, actor, quantity):
    """Record one guarded initial 0-to-N transition for a persisted choice."""
    if business is None or business.pk is None:
        raise ValueError("An existing Business is required.")
    if choice is None or choice.pk is None:
        raise ValueError("An existing ProductChoice is required.")
    if actor is None or actor.pk is None:
        raise ValueError("An authenticated actor is required.")
    if type(quantity) is not int or quantity <= 0:
        raise ValidationError("Initial quantity must be a positive integer.")
    if choice.business_id != business.pk:
        raise ValidationError("Choice must belong to the active Business.")
    if business.owner_id != actor.pk:
        raise ValidationError("Actor must own the active Business.")
    _validate_storable_choice_quantity(quantity)

    with transaction.atomic():
        try:
            locked_choice = (
                ProductChoice.objects.select_for_update()
                .select_related("product")
                .get(pk=choice.pk, business=business)
            )
        except ProductChoice.DoesNotExist as error:
            raise ValidationError(
                "Choice must belong to the active Business."
            ) from error

        if locked_choice.quantity != 0:
            raise ValidationError(
                "Choice quantity must be zero before initialization."
            )
        if InventoryAdjustment.objects.filter(
            business=business,
            choice=locked_choice,
        ).exists():
            raise ValidationError("Choice stock has already been adjusted.")

        locked_choice.quantity = quantity
        locked_choice.save(update_fields=["quantity", "updated_at"])
        adjustment = InventoryAdjustment.objects.create(
            business=business,
            choice=locked_choice,
            actor=actor,
            quantity_before=0,
            quantity_after=quantity,
            delta=quantity,
        )
        is_available = compute_product_availability(
            business=business,
            product=locked_choice.product,
        )

    return ChoiceQuantityInitializationResult(
        choice=locked_choice,
        adjustment=adjustment,
        is_available=is_available,
    )
