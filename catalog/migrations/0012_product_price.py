from decimal import Decimal

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("businesses", "0002_business_default_currency"),
        ("catalog", "0011_product_type_tag_activation"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=12,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(Decimal("0.01"))
                ],
            ),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(
                condition=models.Q(price__isnull=True)
                | (
                    models.Q(price__gt=0)
                    & models.Q(price__lte=Decimal("9999999999.99"))
                ),
                name="product_price_null_or_positive",
            ),
        ),
    ]
