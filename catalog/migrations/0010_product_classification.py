import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0009_remove_legacy_choice_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="product_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="catalog.businessproducttype",
            ),
        ),
        migrations.CreateModel(
            name="ProductTag",
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
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="product_tag_links",
                        to="businesses.business",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tag_links",
                        to="catalog.product",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="product_links",
                        to="catalog.businesstag",
                    ),
                ),
            ],
            options={
                "ordering": ["product_id", "tag_id", "id"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("product", "tag"),
                        name="unique_tag_per_product",
                    ),
                ],
            },
        ),
        migrations.AddField(
            model_name="product",
            name="tags",
            field=models.ManyToManyField(
                blank=True,
                related_name="products",
                through="catalog.ProductTag",
                to="catalog.businesstag",
            ),
        ),
    ]
