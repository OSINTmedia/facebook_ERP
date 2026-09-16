"""Transactional Product archive and restore commands."""

from django.core.exceptions import ValidationError
from django.db import transaction

from catalog.models import Product


def archive_product(*, business, product_id):
    """Archive one owned daily-work Product without changing related truth."""
    return _transition_product(
        business=business,
        product_id=product_id,
        allowed_lifecycles=(Product.Lifecycle.DRAFT, Product.Lifecycle.ACTIVE),
        target_lifecycle=Product.Lifecycle.ARCHIVED,
        invalid_message="Only a Draft or Active Product can be archived.",
    )


def restore_product_to_draft(*, business, product_id):
    """Restore one owned archived Product to Draft for explicit review."""
    return _transition_product(
        business=business,
        product_id=product_id,
        allowed_lifecycles=(Product.Lifecycle.ARCHIVED,),
        target_lifecycle=Product.Lifecycle.DRAFT,
        invalid_message="Only an archived Product can be restored.",
    )


def _transition_product(
    *,
    business,
    product_id,
    allowed_lifecycles,
    target_lifecycle,
    invalid_message,
):
    if business is None or business.pk is None:
        raise ValueError("An existing Business is required.")

    with transaction.atomic():
        product = Product.objects.select_for_update(of=("self",)).get(
            business=business,
            pk=product_id,
        )
        if product.lifecycle not in allowed_lifecycles:
            raise ValidationError(invalid_message)

        product.lifecycle = target_lifecycle
        product.save(update_fields=["lifecycle", "updated_at"])

    return product
