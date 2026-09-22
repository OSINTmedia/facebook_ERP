from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import authenticate, get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from accounts.demo_lifecycle import DEMO_BUSINESS_NAME
from businesses.models import Business
from catalog.models import (
    BusinessProductTypeAlias,
    Product,
    ProductChoice,
    ProductMaterialFact,
    ProductMedia,
)
from catalog.readiness import build_product_buyer_question_coverage
from catalog.ready_reply import build_product_ready_reply
from inventory.availability import compute_product_availability
from inventory.models import InventoryAdjustment


DEMO_EMAIL = "demo-lifecycle@example.test"
DEMO_PASSWORD = "synthetic-demo-password"


class DemoLifecycleCommandTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media_directory = TemporaryDirectory()
        cls._settings_override = override_settings(
            DEMO_ACCESS_ENABLED=True,
            DEMO_USER_EMAIL=DEMO_EMAIL,
            DEMO_USER_PASSWORD=DEMO_PASSWORD,
            MEDIA_ROOT=cls._media_directory.name,
        )
        cls._settings_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._settings_override.disable()
        cls._media_directory.cleanup()
        super().tearDownClass()

    def tearDown(self):
        for path in sorted(
            Path(self._media_directory.name).rglob("*"),
            reverse=True,
        ):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        super().tearDown()

    def stored_files(self):
        return tuple(
            path
            for path in Path(self._media_directory.name).rglob("*")
            if path.is_file()
        )

    def run_action(self, action):
        output = StringIO()
        call_command("demo_lifecycle", action, confirm=True, stdout=output)
        return output.getvalue()

    def demo_business(self):
        return Business.objects.get(
            owner__email=DEMO_EMAIL,
            name=DEMO_BUSINESS_NAME,
        )

    def test_mutation_requires_confirmation_and_dry_run_never_mutates(self):
        with self.assertRaisesMessage(
            CommandError,
            "Demo lifecycle mutations require --confirm",
        ):
            call_command("demo_lifecycle", "seed")

        output = StringIO()
        call_command("demo_lifecycle", "seed", dry_run=True, stdout=output)

        self.assertFalse(get_user_model().objects.exists())
        self.assertFalse(Business.objects.exists())
        self.assertIn("Dry run only", output.getvalue())
        self.assertNotIn(DEMO_PASSWORD, output.getvalue())

    @override_settings(DEMO_ACCESS_ENABLED=False)
    def test_command_refuses_disabled_demo_access(self):
        with self.assertRaisesMessage(CommandError, "Demo access is disabled."):
            call_command("demo_lifecycle", "seed", confirm=True)

    def test_seed_creates_representative_baseline_and_truth(self):
        output = self.run_action("seed")

        business = self.demo_business()
        user = get_user_model().objects.get(email=DEMO_EMAIL)
        self.assertEqual(Product.objects.filter(business=business).count(), 8)
        self.assertEqual(ProductChoice.objects.filter(business=business).count(), 9)
        self.assertEqual(
            Product.objects.filter(
                business=business,
                lifecycle=Product.Lifecycle.ACTIVE,
            ).count(),
            6,
        )
        self.assertEqual(
            Product.objects.filter(
                business=business,
                lifecycle=Product.Lifecycle.DRAFT,
            ).count(),
            1,
        )
        self.assertEqual(
            Product.objects.filter(
                business=business,
                lifecycle=Product.Lifecycle.ARCHIVED,
            ).count(),
            1,
        )
        self.assertTrue(user.check_password(DEMO_PASSWORD))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(business.default_currency, "GEL")
        self.assertEqual(ProductMedia.objects.filter(business=business).count(), 1)
        self.assertEqual(len(self.stored_files()), 1)
        self.assertEqual(
            InventoryAdjustment.objects.filter(business=business).count(),
            7,
        )
        self.assertEqual(
            BusinessProductTypeAlias.objects.get(business=business).alias,
            "dress",
        )

        strong = Product.objects.get(business=business, name="შავი ბამბის კაბა")
        coverage = build_product_buyer_question_coverage(
            business=business,
            product=strong,
        )
        self.assertTrue(all(item.is_answerable for item in coverage.items))
        self.assertIn("129.00 GEL", build_product_ready_reply(
            business=business,
            product=strong,
        ).buyer_text)
        self.assertTrue(
            ProductMaterialFact.objects.filter(
                business=business,
                product=strong,
                confirmation_state=ProductMaterialFact.ConfirmationState.CONFIRMED,
            ).exists()
        )

        weak = Product.objects.get(business=business, name="შესავსები მონახაზი")
        weak_coverage = build_product_buyer_question_coverage(
            business=business,
            product=weak,
        )
        self.assertFalse(any(item.is_answerable for item in weak_coverage.items))
        self.assertIsNone(weak.price)
        self.assertFalse(ProductMedia.objects.filter(product=weak).exists())

        partial = Product.objects.get(business=business, name="ლურჯი კაბა")
        self.assertEqual(
            set(partial.choices.values_list("quantity", flat=True)),
            {0, 4},
        )
        self.assertTrue(
            compute_product_availability(business=business, product=partial)
        )
        sold_out = Product.objects.get(business=business, name="გაყიდული კაბა")
        self.assertFalse(
            compute_product_availability(business=business, product=sold_out)
        )
        duplicate = Product.objects.get(
            business=business,
            name="განმეორებადი არჩევანის კაბა",
        )
        duplicate_choices = list(duplicate.choices.order_by("pk"))
        self.assertEqual(len(duplicate_choices), 2)
        self.assertEqual(duplicate_choices[0].size_id, duplicate_choices[1].size_id)
        self.assertEqual(duplicate_choices[0].color_id, duplicate_choices[1].color_id)
        self.assertNotEqual(duplicate_choices[0].pk, duplicate_choices[1].pk)
        self.assertIn("8 Product(s), 9 choice(s)", output)
        self.assertNotIn(DEMO_PASSWORD, output)

    def test_repeated_seed_replaces_baseline_without_duplicates(self):
        self.run_action("seed")
        business = self.demo_business()
        Product.objects.create(
            business=business,
            name="Temporary seller edit",
            description="Temporary seller edit",
            lifecycle=Product.Lifecycle.DRAFT,
        )

        self.run_action("seed")

        business.refresh_from_db()
        self.assertEqual(Product.objects.filter(business=business).count(), 8)
        self.assertFalse(
            Product.objects.filter(
                business=business,
                name="Temporary seller edit",
            ).exists()
        )
        self.assertEqual(
            Product.objects.filter(
                business=business,
                name="შავი ბამბის კაბა",
            ).count(),
            1,
        )
        self.assertEqual(len(self.stored_files()), 1)

    def test_reset_preserves_demo_identity_login_and_other_business_data(self):
        self.run_action("seed")
        demo_user = get_user_model().objects.get(email=DEMO_EMAIL)
        demo_business = self.demo_business()
        other_owner = get_user_model().objects.create_user(
            email="other-owner@example.test",
            password="other-password",
        )
        other_business = Business.objects.create(
            owner=other_owner,
            name="Other Business",
        )
        other_product = Product.objects.create(
            business=other_business,
            name="Other Product",
            description="Must survive demo reset",
            lifecycle=Product.Lifecycle.DRAFT,
        )

        output = self.run_action("reset")

        self.assertTrue(get_user_model().objects.filter(pk=demo_user.pk).exists())
        self.assertTrue(Business.objects.filter(pk=demo_business.pk).exists())
        self.assertFalse(Product.objects.filter(business=demo_business).exists())
        self.assertFalse(ProductChoice.objects.filter(business=demo_business).exists())
        self.assertFalse(
            InventoryAdjustment.objects.filter(business=demo_business).exists()
        )
        self.assertTrue(Product.objects.filter(pk=other_product.pk).exists())
        self.assertEqual(self.stored_files(), ())
        self.assertIsNotNone(
            authenticate(email=DEMO_EMAIL, password=DEMO_PASSWORD)
        )
        self.assertIn("0 Product(s), 0 choice(s)", output)

    def test_reseed_restores_known_baseline_after_workflow_changes(self):
        self.run_action("seed")
        business = self.demo_business()
        business.default_currency = "USD"
        business.save(update_fields=["default_currency", "updated_at"])
        Product.objects.filter(
            business=business,
            name="შავი ბამბის კაბა",
        ).update(description="Changed during review")
        Product.objects.filter(
            business=business,
            name="შესავსები მონახაზი",
        ).delete()

        self.run_action("reseed")

        self.assertEqual(Product.objects.filter(business=business).count(), 8)
        business.refresh_from_db()
        self.assertEqual(business.default_currency, "GEL")
        self.assertEqual(
            Product.objects.get(
                business=business,
                name="შავი ბამბის კაბა",
            ).description,
            "შავი ბამბის კაბა საღამოსთვის",
        )
        self.assertTrue(
            Product.objects.filter(
                business=business,
                name="შესავსები მონახაზი",
            ).exists()
        )
        self.assertEqual(len(self.stored_files()), 1)

    def test_ambiguous_demo_business_identity_is_refused_without_mutation(self):
        user = get_user_model().objects.create_user(
            email=DEMO_EMAIL,
            password=DEMO_PASSWORD,
        )
        first = Business.objects.create(owner=user, name=DEMO_BUSINESS_NAME)
        second = Business.objects.create(owner=user, name=DEMO_BUSINESS_NAME)
        Product.objects.create(
            business=first,
            name="First protected Product",
            description="First",
        )
        Product.objects.create(
            business=second,
            name="Second protected Product",
            description="Second",
        )

        with self.assertRaisesMessage(
            CommandError,
            "configured demo user owns multiple Businesses",
        ):
            call_command("demo_lifecycle", "reseed", confirm=True)

        self.assertEqual(Product.objects.count(), 2)
        user.refresh_from_db()
        self.assertTrue(user.check_password(DEMO_PASSWORD))

    def test_seed_reuses_demo_users_only_business_without_renaming_it(self):
        user = get_user_model().objects.create_user(
            email=DEMO_EMAIL,
            password=DEMO_PASSWORD,
        )
        existing = Business.objects.create(owner=user, name="Existing Business")
        existing_id = existing.pk

        self.run_action("seed")

        self.assertEqual(list(user.businesses.all()), [existing])
        existing.refresh_from_db()
        self.assertEqual(existing.pk, existing_id)
        self.assertEqual(existing.owner_id, user.pk)
        self.assertEqual(existing.name, "Existing Business")
        self.assertEqual(Product.objects.filter(business=existing).count(), 8)

    def test_media_cleanup_failure_is_reported_after_scoped_database_reset(self):
        self.run_action("seed")
        business = self.demo_business()

        with patch(
            "accounts.demo_lifecycle._StoredMedia.delete",
            side_effect=OSError("storage unavailable"),
        ):
            with self.assertRaisesMessage(
                CommandError,
                "scoped media cleanup failed for 1 file(s)",
            ):
                call_command("demo_lifecycle", "reset", confirm=True)

        self.assertFalse(Product.objects.filter(business=business).exists())

    def test_seed_failure_rolls_back_database_and_discards_new_media(self):
        from accounts import demo_lifecycle

        real_create_product = demo_lifecycle._create_product
        calls = 0

        def fail_after_first_product(**kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("synthetic seed failure")
            return real_create_product(**kwargs)

        with patch(
            "accounts.demo_lifecycle._create_product",
            side_effect=fail_after_first_product,
        ):
            with self.assertRaisesMessage(RuntimeError, "synthetic seed failure"):
                call_command("demo_lifecycle", "seed", confirm=True)

        self.assertFalse(get_user_model().objects.exists())
        self.assertFalse(Business.objects.exists())
        self.assertFalse(Product.objects.exists())
        self.assertEqual(self.stored_files(), ())
