from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update the explicitly enabled synthetic demo seller account."

    def handle(self, *args, **options):
        if not settings.DEMO_ACCESS_ENABLED:
            raise CommandError("Demo access is disabled.")

        if not settings.DEMO_USER_EMAIL.strip() or not settings.DEMO_USER_PASSWORD:
            raise CommandError(
                "DEMO_USER_EMAIL and DEMO_USER_PASSWORD must be configured."
            )

        user_model = get_user_model()
        email = user_model.objects.normalize_email(settings.DEMO_USER_EMAIL).lower()

        try:
            user = user_model.objects.get(email=email)
            action = "updated"
        except user_model.DoesNotExist:
            user = user_model(email=email)
            action = "created"

        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        user.set_password(settings.DEMO_USER_PASSWORD)
        user.save()

        self.stdout.write(self.style.SUCCESS(f"Demo user {action}."))
