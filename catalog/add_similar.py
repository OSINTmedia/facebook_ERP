"""Atomic Add Similar command for confirmed Product truth."""

from django.core.exceptions import ValidationError
from django.db import transaction

from catalog.models import (
    Product,
    ProductChoice,
    ProductMaterialFact,
    ProductTag,
)


def add_similar_product(*, business, source_product_id):
    """Copy one owned Product into a zero-stock Draft with new identities."""
    if business is None or business.pk is None:
        raise ValueError("An existing Business is required.")

    with transaction.atomic():
        source = (
            Product.objects.select_for_update(of=("self",))
            .select_related("product_type")
            .exclude(lifecycle=Product.Lifecycle.ARCHIVED)
            .get(business=business, pk=source_product_id)
        )
        _validate_product_type_scope(source, business)

        destination = Product(
            business=business,
            product_type=source.product_type,
            name=source.name,
            description=source.description,
            price=source.price,
            lifecycle=Product.Lifecycle.DRAFT,
        )
        destination.full_clean()
        destination.save()

        _copy_tags(source=source, destination=destination, business=business)
        _copy_materials(
            source=source,
            destination=destination,
            business=business,
        )
        _copy_active_choices(
            source=source,
            destination=destination,
            business=business,
        )

    return destination


def _validate_product_type_scope(source, business):
    if (
        source.product_type_id
        and source.product_type.business_id != business.pk
    ):
        raise ValidationError("Product type must belong to the active Business.")


def _copy_tags(*, source, destination, business):
    links = list(
        ProductTag.objects.select_for_update()
        .select_related("tag")
        .filter(product=source)
        .order_by("id")
    )
    for source_link in links:
        if (
            source_link.business_id != business.pk
            or source_link.tag.business_id != business.pk
        ):
            raise ValidationError("Tags must belong to the active Business.")
        destination_link = ProductTag(
            business=business,
            product=destination,
            tag=source_link.tag,
        )
        destination_link.full_clean()
        destination_link.save()


def _copy_materials(*, source, destination, business):
    material_facts = list(
        ProductMaterialFact.objects.select_for_update()
        .filter(product=source)
        .order_by("id")
    )
    for source_fact in material_facts:
        if source_fact.business_id != business.pk:
            raise ValidationError(
                "Material facts must belong to the active Business."
            )
        destination_fact = ProductMaterialFact(
            business=business,
            product=destination,
            canonical_material=source_fact.canonical_material,
            percentage=source_fact.percentage,
            original_text=source_fact.original_text,
            source=source_fact.source,
            confirmation_state=source_fact.confirmation_state,
        )
        destination_fact.full_clean()
        destination_fact.save()


def _copy_active_choices(*, source, destination, business):
    choices = list(
        ProductChoice.objects.select_for_update()
        .select_related("size", "color")
        .filter(product=source, is_active=True)
        .order_by("id")
    )
    for source_choice in choices:
        if (
            source_choice.business_id != business.pk
            or source_choice.size.business_id != business.pk
            or source_choice.color.business_id != business.pk
        ):
            raise ValidationError("Choices must belong to the active Business.")
        destination_choice = ProductChoice(
            business=business,
            product=destination,
            size=source_choice.size,
            color=source_choice.color,
            quantity=0,
            is_active=True,
        )
        destination_choice.full_clean()
        destination_choice.save()
