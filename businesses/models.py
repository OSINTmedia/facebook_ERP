from django.conf import settings
from django.db import models


class Business(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="businesses",
    )
    name = models.CharField(max_length=120)
    default_currency = models.CharField(max_length=3, default="GEL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]
        verbose_name_plural = "businesses"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(default_currency__regex=r"^[A-Z]{3}$"),
                name="business_currency_code_format",
            ),
        ]

    def __str__(self):
        return self.name
