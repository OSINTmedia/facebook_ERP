"""Business-scoped creation boundary for controlled Size/Color vocabulary."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.functions import Lower, Trim

from businesses.models import Business
from catalog.models import (
    BusinessColor,
    BusinessColorAlias,
    BusinessSize,
    BusinessSizeAlias,
)


SIZE_VOCABULARY = "size"
COLOR_VOCABULARY = "color"


@transaction.atomic
def create_choice_vocabulary_entry(*, business, kind, name, aliases=()):
    """Create one canonical value and its explicitly approved aliases atomically."""
    if business is None or business.pk is None:
        raise ValueError("An existing Business is required.")

    business = Business.objects.select_for_update().get(pk=business.pk)

    if kind == SIZE_VOCABULARY:
        canonical_model = BusinessSize
        alias_model = BusinessSizeAlias
        relation_name = "size"
    elif kind == COLOR_VOCABULARY:
        canonical_model = BusinessColor
        alias_model = BusinessColorAlias
        relation_name = "color"
    else:
        raise ValueError("Choice vocabulary kind must be size or color.")

    try:
        normalized_name = (name or "").strip()
        canonical = (
            canonical_model.objects.filter(business=business)
            .annotate(normalized_name=Lower(Trim("name")))
            .filter(normalized_name=normalized_name.casefold())
            .first()
        )
        if canonical is None:
            canonical = canonical_model(business=business, name=normalized_name)
            canonical.full_clean()
            canonical.save()
        elif not canonical.is_active:
            canonical.is_active = True
            canonical.save(update_fields=["is_active", "updated_at"])

        for alias_value in aliases:
            normalized_alias = alias_value.strip()
            existing_alias = (
                alias_model.objects.filter(business=business)
                .annotate(normalized_alias=Lower(Trim("alias")))
                .filter(normalized_alias=normalized_alias.casefold())
                .first()
            )
            if existing_alias is not None:
                if getattr(existing_alias, f"{relation_name}_id") == canonical.pk:
                    continue
                raise ValidationError(
                    {"aliases": f'Alias "{normalized_alias}" is already assigned.'}
                )

            alias = alias_model(
                business=business,
                alias=normalized_alias,
                **{relation_name: canonical},
            )
            alias.full_clean()
            alias.save()
    except IntegrityError as exc:
        raise ValidationError(
            {"name": "This canonical value or one of its aliases already exists."}
        ) from exc

    return canonical


@transaction.atomic
def update_choice_vocabulary_entry(
    *,
    business,
    kind,
    entry_id,
    name,
    aliases=(),
    is_active=True,
):
    """Atomically update one scoped canonical value and replace its aliases."""
    if business is None or business.pk is None:
        raise ValueError("An existing Business is required.")

    business = Business.objects.select_for_update().get(pk=business.pk)

    if kind == SIZE_VOCABULARY:
        canonical_model = BusinessSize
        alias_model = BusinessSizeAlias
        relation_name = "size"
    elif kind == COLOR_VOCABULARY:
        canonical_model = BusinessColor
        alias_model = BusinessColorAlias
        relation_name = "color"
    else:
        raise ValueError("Choice vocabulary kind must be size or color.")

    try:
        canonical = canonical_model.objects.select_for_update().get(
            business=business,
            pk=entry_id,
        )
    except canonical_model.DoesNotExist as exc:
        raise ValidationError(
            {"name": "Vocabulary entry was not found for this Business."}
        ) from exc

    try:
        list(
            alias_model.objects.select_for_update().filter(
                business=business,
            )
        )
        canonical.aliases.all().delete()
        canonical.name = (name or "").strip()
        canonical.is_active = bool(is_active)
        canonical.full_clean()
        canonical.save()

        for alias_value in aliases:
            alias = alias_model(
                business=business,
                alias=alias_value.strip(),
                **{relation_name: canonical},
            )
            alias.full_clean()
            alias.save()
    except IntegrityError as exc:
        raise ValidationError(
            {"name": "This canonical value or one of its aliases already exists."}
        ) from exc

    return canonical
