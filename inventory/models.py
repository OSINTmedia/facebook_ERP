from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from businesses.models import Business
from catalog.models import ProductChoice


class InventoryAdjustmentQuerySet(models.QuerySet):
    def bulk_create(
        self,
        objs,
        batch_size=None,
        ignore_conflicts=False,
        update_conflicts=False,
        update_fields=None,
        unique_fields=None,
    ):
        if (
            ignore_conflicts
            or update_conflicts
            or update_fields
            or unique_fields
        ):
            raise ValidationError(
                "Inventory adjustment conflict handling is not allowed."
            )

        adjustments = list(objs)
        for adjustment in adjustments:
            adjustment._validate_business_scope()

        return super().bulk_create(
            adjustments,
            batch_size=batch_size,
        )

    def update(self, **kwargs):
        raise ValidationError("Inventory adjustments cannot be changed.")

    def delete(self):
        raise ValidationError("Inventory adjustments cannot be deleted.")


class InventoryAdjustment(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="inventory_adjustments",
    )
    choice = models.ForeignKey(
        ProductChoice,
        on_delete=models.PROTECT,
        related_name="inventory_adjustments",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="inventory_adjustments",
    )
    quantity_before = models.PositiveIntegerField()
    quantity_after = models.PositiveIntegerField()
    delta = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = InventoryAdjustmentQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity_before__gte=0),
                name="inventory_adjustment_before_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity_after__gte=0),
                name="inventory_adjustment_after_nonnegative",
            ),
            models.CheckConstraint(
                condition=~models.Q(delta=0),
                name="inventory_adjustment_delta_nonzero",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    quantity_after=models.F("quantity_before") + models.F("delta")
                ),
                name="inventory_adjustment_quantity_consistent",
            ),
        ]

    def clean(self):
        super().clean()
        self._validate_business_scope()
        self._validate_quantities()

    def save(self, *args, **kwargs):
        if self.pk is not None and type(self).objects.filter(pk=self.pk).exists():
            raise ValidationError("Inventory adjustments cannot be changed.")
        self._validate_business_scope()
        self._validate_quantities()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Inventory adjustments cannot be deleted.")

    def _validate_business_scope(self):
        if (
            self.business_id
            and self.choice_id
            and self.choice.business_id != self.business_id
        ):
            raise ValidationError(
                {"choice": "Choice must belong to the active Business."}
            )
        if (
            self.business_id
            and self.actor_id
            and self.business.owner_id != self.actor_id
        ):
            raise ValidationError(
                {"actor": "Actor must own the active Business."}
            )

    def _validate_quantities(self):
        if self.quantity_before is None or self.quantity_before < 0:
            raise ValidationError(
                {"quantity_before": "Starting quantity cannot be negative."}
            )
        if self.quantity_after is None or self.quantity_after < 0:
            raise ValidationError(
                {"quantity_after": "Resulting quantity cannot be negative."}
            )
        if self.delta in (None, 0):
            raise ValidationError({"delta": "Adjustment delta cannot be zero."})
        if self.quantity_after != self.quantity_before + self.delta:
            raise ValidationError(
                {"delta": "Adjustment quantities and delta must be consistent."}
            )

    def __str__(self):
        return (
            f"{self.choice}: {self.quantity_before} -> "
            f"{self.quantity_after} ({self.delta:+d})"
        )
