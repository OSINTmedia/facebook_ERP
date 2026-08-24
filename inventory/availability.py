"""Computed Product availability from stored lifecycle and choice stock truth."""

from django.core.exceptions import ValidationError

from catalog.models import Product


def compute_product_availability(*, business, product) -> bool:
    """Return availability for one persisted Product in the active Business."""
    if business is None or business.pk is None:
        raise ValueError("An existing Business is required.")
    if product is None or product.pk is None:
        raise ValueError("An existing Product is required.")
    if product.business_id != business.pk:
        raise ValidationError("Product must belong to the active Business.")
    if product.lifecycle != Product.Lifecycle.ACTIVE:
        return False

    return product.choices.filter(
        business=business,
        is_active=True,
        quantity__gt=0,
    ).exists()
