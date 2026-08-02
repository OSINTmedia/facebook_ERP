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

    def save(self, *args, **kwargs):
        self.name = (self.name or "").strip()
        if not self.name:
            raise ValidationError({"name": "Product type name is required."})
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

    def save(self, *args, **kwargs):
        self.name = (self.name or "").strip()
        if not self.name:
            raise ValidationError({"name": "Tag name is required."})
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


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
