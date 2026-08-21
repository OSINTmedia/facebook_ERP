from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0010_product_classification"),
    ]

    operations = [
        migrations.AddField(
            model_name="businessproducttype",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="businesstag",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
