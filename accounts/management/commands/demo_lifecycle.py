from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from accounts.demo_lifecycle import (
    DemoLifecycleError,
    apply_demo_lifecycle,
    preview_demo_lifecycle,
)


class Command(BaseCommand):
    help = "Seed, reset, or reseed the explicitly configured synthetic demo."

    def add_arguments(self, parser):
        parser.add_argument("action", choices=("seed", "reset", "reseed"))
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirm the scoped demo mutation.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Describe the scoped action without changing data.",
        )

    def handle(self, *args, **options):
        action = options["action"]
        dry_run = options["dry_run"]
        if not dry_run and not options["confirm"]:
            raise CommandError(
                "Demo lifecycle mutations require --confirm; use --dry-run to preview."
            )

        try:
            if dry_run:
                result = preview_demo_lifecycle(action=action)
                self.stdout.write(
                    "Dry run only: "
                    f"{action} targets {result.products} Product(s) and "
                    f"{result.choices} choice(s) in the protected demo Business."
                )
                return
            result = apply_demo_lifecycle(action=action)
        except (DemoLifecycleError, ValidationError) as error:
            raise CommandError(str(error)) from error

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo {action} complete: {result.products} Product(s), "
                f"{result.choices} choice(s)."
            )
        )
