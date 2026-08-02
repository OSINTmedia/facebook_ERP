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
