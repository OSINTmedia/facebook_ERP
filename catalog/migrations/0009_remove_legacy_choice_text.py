from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0008_controlled_size_color_vocabulary"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="productchoice",
            name="legacy_size_text",
        ),
        migrations.RemoveField(
            model_name="productchoice",
            name="legacy_color_text",
        ),
    ]
