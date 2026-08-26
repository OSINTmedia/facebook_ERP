"""Computed Product availability from stored lifecycle and choice stock truth."""

from django.core.exceptions import ValidationError

from catalog.models import Product


def compute_availability_from_stock_state(
    *,
    product_lifecycle,
    has_positive_active_choice,
) -> bool:
    """Return computed availability from already-read Product and choice state."""

    return (
        product_lifecycle == Product.Lifecycle.ACTIVE
        and bool(has_positive_active_choice)
    )


def compute_product_availability(*, business, product) -> bool:
    """Return availability for one persisted Product in the active Business."""
    if business is None or business.pk is None:
        raise ValueError("An existing Business is required.")
    if product is None or product.pk is None:
        raise ValueError("An existing Product is required.")
    if product.business_id != business.pk:
        raise ValidationError("Product must belong to the active Business.")
    has_positive_active_choice = False
    if product.lifecycle == Product.Lifecycle.ACTIVE:
        has_positive_active_choice = product.choices.filter(
            business=business,
            is_active=True,
            quantity__gt=0,
        ).exists()

    return compute_availability_from_stock_state(
        product_lifecycle=product.lifecycle,
        has_positive_active_choice=has_positive_active_choice,
    )
