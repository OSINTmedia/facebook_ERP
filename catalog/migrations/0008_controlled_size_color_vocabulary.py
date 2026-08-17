import django.db.models.deletion
from django.db import migrations, models
from django.db.models.functions import Lower, Trim


def _canonical_for_text(model, cache, *, business_id, value, field_label):
    canonical_name = (value or "").strip()
    if not canonical_name:
        raise RuntimeError(f"Cannot migrate a blank ProductChoice {field_label}.")

    cache_key = (business_id, canonical_name.casefold())
    canonical = cache.get(cache_key)
    if canonical is None:
        canonical = model.objects.create(
            business_id=business_id,
            name=canonical_name,
            is_active=True,
        )
        cache[cache_key] = canonical
    return canonical


def migrate_choice_text_to_vocabulary(apps, schema_editor):
    ProductChoice = apps.get_model("catalog", "ProductChoice")
    BusinessSize = apps.get_model("catalog", "BusinessSize")
    BusinessColor = apps.get_model("catalog", "BusinessColor")
    size_cache = {}
    color_cache = {}

    for choice in ProductChoice.objects.order_by("id").iterator():
        size = _canonical_for_text(
            BusinessSize,
            size_cache,
            business_id=choice.business_id,
            value=choice.legacy_size_text,
            field_label="size",
        )
        color = _canonical_for_text(
            BusinessColor,
            color_cache,
            business_id=choice.business_id,
            value=choice.legacy_color_text,
            field_label="color",
        )
        ProductChoice.objects.filter(pk=choice.pk).update(
            size_id=size.pk,
            color_id=color.pk,
        )


def restore_choice_text_from_vocabulary(apps, schema_editor):
    ProductChoice = apps.get_model("catalog", "ProductChoice")

    for choice in ProductChoice.objects.select_related("size", "color").iterator():
        ProductChoice.objects.filter(pk=choice.pk).update(
            legacy_size_text=choice.size.name,
            legacy_color_text=choice.color.name,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0007_remove_unique_product_choice_per_product"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="productchoice",
            name="product_choice_size_not_blank",
        ),
        migrations.RemoveConstraint(
            model_name="productchoice",
            name="product_choice_color_not_blank",
        ),
        migrations.RenameField(
            model_name="productchoice",
            old_name="size",
            new_name="legacy_size_text",
        ),
        migrations.RenameField(
            model_name="productchoice",
            old_name="color",
            new_name="legacy_color_text",
        ),
        migrations.AlterField(
            model_name="productchoice",
            name="legacy_size_text",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=40,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="productchoice",
            name="legacy_color_text",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=80,
                null=True,
            ),
        ),
        migrations.CreateModel(
            name="BusinessSize",
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
                ("name", models.CharField(max_length=40)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sizes",
                        to="businesses.business",
                    ),
                ),
            ],
            options={
                "ordering": ["name", "id"],
                "constraints": [
                    models.UniqueConstraint(
                        models.F("business"),
                        Lower(Trim("name")),
                        name="unique_size_name_per_business",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("name__regex", "\\S")),
                        name="size_name_not_blank",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="BusinessColor",
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
                ("name", models.CharField(max_length=80)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="colors",
                        to="businesses.business",
                    ),
                ),
            ],
            options={
                "ordering": ["name", "id"],
                "constraints": [
                    models.UniqueConstraint(
                        models.F("business"),
                        Lower(Trim("name")),
                        name="unique_color_name_per_business",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("name__regex", "\\S")),
                        name="color_name_not_blank",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="BusinessSizeAlias",
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
                ("alias", models.CharField(max_length=80)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="size_aliases",
                        to="businesses.business",
                    ),
                ),
                (
                    "size",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aliases",
                        to="catalog.businesssize",
                    ),
                ),
            ],
            options={
                "ordering": ["alias", "id"],
                "constraints": [
                    models.UniqueConstraint(
                        models.F("business"),
                        Lower(Trim("alias")),
                        name="unique_size_alias_per_business",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("alias__regex", "\\S")),
                        name="size_alias_not_blank",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="BusinessColorAlias",
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
                ("alias", models.CharField(max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="color_aliases",
                        to="businesses.business",
                    ),
                ),
                (
                    "color",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aliases",
                        to="catalog.businesscolor",
                    ),
                ),
            ],
            options={
                "ordering": ["alias", "id"],
                "constraints": [
                    models.UniqueConstraint(
                        models.F("business"),
                        Lower(Trim("alias")),
                        name="unique_color_alias_per_business",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("alias__regex", "\\S")),
                        name="color_alias_not_blank",
                    ),
                ],
            },
        ),
        migrations.AddField(
            model_name="productchoice",
            name="size",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="product_choices",
                to="catalog.businesssize",
            ),
        ),
        migrations.AddField(
            model_name="productchoice",
            name="color",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="product_choices",
                to="catalog.businesscolor",
            ),
        ),
        migrations.RunPython(
            migrate_choice_text_to_vocabulary,
            restore_choice_text_from_vocabulary,
        ),
        migrations.AlterField(
            model_name="productchoice",
            name="size",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="product_choices",
                to="catalog.businesssize",
            ),
        ),
        migrations.AlterField(
            model_name="productchoice",
            name="color",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="product_choices",
                to="catalog.businesscolor",
            ),
        ),
        migrations.AlterModelOptions(
            name="productchoice",
            options={"ordering": ["product_id", "size_id", "color_id", "id"]},
        ),
    ]
