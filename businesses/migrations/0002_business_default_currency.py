from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("businesses", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="business",
            name="default_currency",
            field=models.CharField(default="GEL", max_length=3),
        ),
        migrations.AddConstraint(
            model_name="business",
            constraint=models.CheckConstraint(
                condition=models.Q(default_currency__regex=r"^[A-Z]{3}$"),
                name="business_currency_code_format",
            ),
        ),
    ]
