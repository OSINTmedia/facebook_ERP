import catalog.product_media
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0012_product_price"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductMedia",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        max_length=255,
                        upload_to=catalog.product_media.product_media_upload_to,
                        validators=[
                            catalog.product_media.validate_product_media_file
                        ],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="product_media",
                        to="businesses.business",
                    ),
                ),
                (
                    "product",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="primary_media",
                        to="catalog.product",
                    ),
                ),
            ],
            options={
                "ordering": ["product_id", "id"],
            },
        ),
    ]
