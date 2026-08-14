from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower, Trim

from businesses.models import Business


class BusinessProductType(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="product_types",
    )
    name = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(
                "business",
                Lower(Trim("name")),
                name="unique_product_type_name_per_business",
            ),
            models.CheckConstraint(
                condition=models.Q(name__regex=r"\S"),
                name="product_type_name_not_blank",
            ),
        ]

    def clean(self):
        super().clean()
        self.name = (self.name or "").strip()
        if not self.name:
            raise ValidationError({"name": "Product type name is required."})
        if _product_type_alias_exists(self.business_id, self.name):
            raise ValidationError(
                {"name": "Product type name conflicts with an existing alias."}
            )

    def save(self, *args, **kwargs):
        self.name = (self.name or "").strip()
        if not self.name:
            raise ValidationError({"name": "Product type name is required."})
        if _product_type_alias_exists(self.business_id, self.name):
            raise ValidationError(
                {"name": "Product type name conflicts with an existing alias."}
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BusinessTag(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="tags",
    )
    name = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(
                "business",
                Lower(Trim("name")),
                name="unique_tag_name_per_business",
            ),
            models.CheckConstraint(
                condition=models.Q(name__regex=r"\S"),
                name="tag_name_not_blank",
            ),
        ]

    def clean(self):
        super().clean()
        self.name = (self.name or "").strip()
        if not self.name:
            raise ValidationError({"name": "Tag name is required."})
        if _tag_alias_exists(self.business_id, self.name):
            raise ValidationError({"name": "Tag name conflicts with an existing alias."})

    def save(self, *args, **kwargs):
        self.name = (self.name or "").strip()
        if not self.name:
            raise ValidationError({"name": "Tag name is required."})
        if _tag_alias_exists(self.business_id, self.name):
            raise ValidationError({"name": "Tag name conflicts with an existing alias."})
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BusinessProductTypeAlias(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="product_type_aliases",
    )
    product_type = models.ForeignKey(
        BusinessProductType,
        on_delete=models.PROTECT,
        related_name="aliases",
    )
    alias = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["alias", "id"]
        constraints = [
            models.UniqueConstraint(
                "business",
                Lower(Trim("alias")),
                name="unique_product_type_alias_per_business",
            ),
            models.CheckConstraint(
                condition=models.Q(alias__regex=r"\S"),
                name="product_type_alias_not_blank",
            ),
        ]

    def clean(self):
        super().clean()
        self.alias = _normalized_alias(self.alias, "Product type alias is required.")
        self._validate_business_scope()
        if _product_type_name_exists(self.business_id, self.alias):
            raise ValidationError(
                {"alias": "Alias conflicts with an existing product type name."}
            )

    def save(self, *args, **kwargs):
        self.alias = _normalized_alias(self.alias, "Product type alias is required.")
        self._validate_business_scope()
        if _product_type_name_exists(self.business_id, self.alias):
            raise ValidationError(
                {"alias": "Alias conflicts with an existing product type name."}
            )
        super().save(*args, **kwargs)

    def _validate_business_scope(self):
        if (
            self.business_id
            and self.product_type_id
            and self.product_type.business_id != self.business_id
        ):
            raise ValidationError(
                {"product_type": "Product type must belong to the same Business."}
            )

    def __str__(self):
        return self.alias


class BusinessTagAlias(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="tag_aliases",
    )
    tag = models.ForeignKey(
        BusinessTag,
        on_delete=models.PROTECT,
        related_name="aliases",
    )
    alias = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["alias", "id"]
        constraints = [
            models.UniqueConstraint(
                "business",
                Lower(Trim("alias")),
                name="unique_tag_alias_per_business",
            ),
            models.CheckConstraint(
                condition=models.Q(alias__regex=r"\S"),
                name="tag_alias_not_blank",
            ),
        ]

    def clean(self):
        super().clean()
        self.alias = _normalized_alias(self.alias, "Tag alias is required.")
        self._validate_business_scope()
        if _tag_name_exists(self.business_id, self.alias):
            raise ValidationError({"alias": "Alias conflicts with an existing tag name."})

    def save(self, *args, **kwargs):
        self.alias = _normalized_alias(self.alias, "Tag alias is required.")
        self._validate_business_scope()
        if _tag_name_exists(self.business_id, self.alias):
            raise ValidationError({"alias": "Alias conflicts with an existing tag name."})
        super().save(*args, **kwargs)

    def _validate_business_scope(self):
        if self.business_id and self.tag_id and self.tag.business_id != self.business_id:
            raise ValidationError({"tag": "Tag must belong to the same Business."})

    def __str__(self):
        return self.alias


class Product(models.Model):
    class Lifecycle(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"

    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="products",
    )
    name = models.CharField(max_length=160)
    description = models.TextField()
    lifecycle = models.CharField(
        max_length=20,
        choices=Lifecycle.choices,
        default=Lifecycle.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name


class ProductChoice(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="product_choices",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="choices",
    )
    size = models.CharField(max_length=40)
    color = models.CharField(max_length=80)
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["product_id", "size", "color", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(size__regex=r"\S"),
                name="product_choice_size_not_blank",
            ),
            models.CheckConstraint(
                condition=models.Q(color__regex=r"\S"),
                name="product_choice_color_not_blank",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=0),
                name="product_choice_quantity_nonnegative",
            ),
        ]

    def clean(self):
        super().clean()
        self._normalize_fields()
        self._validate_business_scope()
        self._validate_quantity()

    def save(self, *args, **kwargs):
        self._normalize_fields()
        self._validate_business_scope()
        self._validate_quantity()
        super().save(*args, **kwargs)

    def _normalize_fields(self):
        self.size = _normalized_required_text(
            self.size,
            "size",
            "Choice size is required.",
        )
        self.color = _normalized_required_text(
            self.color,
            "color",
            "Choice color is required.",
        )

    def _validate_business_scope(self):
        if (
            self.business_id
            and self.product_id
            and self.product.business_id != self.business_id
        ):
            raise ValidationError(
                {"product": "Product must belong to the same Business."}
            )

    def _validate_quantity(self):
        if self.quantity is None or self.quantity < 0:
            raise ValidationError(
                {"quantity": "Choice quantity cannot be negative."}
            )

    def __str__(self):
        return f"{self.product}: {self.size} / {self.color}"


class ProductMaterialFact(models.Model):
    class Source(models.TextChoices):
        DESCRIPTION = "description", "Description"
        MANUAL = "manual", "Manual"

    class ConfirmationState(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"

    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="product_material_facts",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="material_facts",
    )
    canonical_material = models.CharField(max_length=80)
    percentage = models.PositiveSmallIntegerField(null=True, blank=True)
    original_text = models.CharField(max_length=160)
    source = models.CharField(max_length=20, choices=Source.choices)
    confirmation_state = models.CharField(
        max_length=20,
        choices=ConfirmationState.choices,
        default=ConfirmationState.CONFIRMED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["product_id", "canonical_material", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(canonical_material__regex=r"\S"),
                name="material_canonical_not_blank",
            ),
            models.CheckConstraint(
                condition=models.Q(original_text__regex=r"\S"),
                name="material_original_text_not_blank",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(percentage__isnull=True)
                    | (models.Q(percentage__gte=1) & models.Q(percentage__lte=100))
                ),
                name="material_percentage_1_to_100_or_null",
            ),
            models.CheckConstraint(
                condition=models.Q(source__in=["description", "manual"]),
                name="material_source_known",
            ),
            models.CheckConstraint(
                condition=models.Q(confirmation_state="confirmed"),
                name="material_confirmation_state_confirmed",
            ),
        ]

    def clean(self):
        super().clean()
        self._normalize_fields()
        self._validate_business_scope()
        self._validate_percentage()
        self._validate_source()
        self._validate_confirmation_state()

    def save(self, *args, **kwargs):
        self._normalize_fields()
        self._validate_business_scope()
        self._validate_percentage()
        self._validate_source()
        self._validate_confirmation_state()
        super().save(*args, **kwargs)

    def _normalize_fields(self):
        self.canonical_material = _normalized_required_text(
            self.canonical_material,
            "canonical_material",
            "Canonical material is required.",
        )
        self.original_text = _normalized_required_text(
            self.original_text,
            "original_text",
            "Original material wording is required.",
        )
        self.source = (self.source or "").strip()
        self.confirmation_state = (self.confirmation_state or "").strip()

    def _validate_business_scope(self):
        if (
            self.business_id
            and self.product_id
            and self.product.business_id != self.business_id
        ):
            raise ValidationError(
                {"product": "Product must belong to the same Business."}
            )

    def _validate_percentage(self):
        if self.percentage is not None and not 1 <= self.percentage <= 100:
            raise ValidationError(
                {"percentage": "Material percentage must be between 1 and 100."}
            )

    def _validate_source(self):
        if self.source not in self.Source.values:
            raise ValidationError({"source": "Material source is required."})

    def _validate_confirmation_state(self):
        if self.confirmation_state != self.ConfirmationState.CONFIRMED:
            raise ValidationError(
                {"confirmation_state": "Material fact must be confirmed."}
            )

    def __str__(self):
        return self.canonical_material


def _normalized_alias(value, message):
    normalized = (value or "").strip()
    if not normalized:
        raise ValidationError({"alias": message})
    return normalized


def _normalized_text_exists(queryset, field_name, value):
    normalized = (value or "").strip().casefold()
    if not normalized:
        return False
    return (
        queryset.annotate(normalized_value=Lower(Trim(field_name)))
        .filter(normalized_value=normalized)
        .exists()
    )


def _normalized_required_text(value, field_name, message):
    normalized = (value or "").strip()
    if not normalized:
        raise ValidationError({field_name: message})
    return normalized


def _product_type_name_exists(business_id, value):
    if not business_id:
        return False
    return _normalized_text_exists(
        BusinessProductType.objects.filter(business_id=business_id),
        "name",
        value,
    )


def _tag_name_exists(business_id, value):
    if not business_id:
        return False
    return _normalized_text_exists(
        BusinessTag.objects.filter(business_id=business_id),
        "name",
        value,
    )


def _product_type_alias_exists(business_id, value):
    if not business_id or "BusinessProductTypeAlias" not in globals():
        return False
    return _normalized_text_exists(
        BusinessProductTypeAlias.objects.filter(business_id=business_id),
        "alias",
        value,
    )


def _tag_alias_exists(business_id, value):
    if not business_id or "BusinessTagAlias" not in globals():
        return False
    return _normalized_text_exists(
        BusinessTagAlias.objects.filter(business_id=business_id),
        "alias",
        value,
    )
