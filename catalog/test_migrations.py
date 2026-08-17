from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class ControlledSizeColorVocabularyMigrationTests(TransactionTestCase):
    migrate_from = ("catalog", "0007_remove_unique_product_choice_per_product")
    migrate_to = ("catalog", "0009_remove_legacy_choice_text")
    reset_sequences = True

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.executor.migrate([self.migrate_from])
        old_apps = self.executor.loader.project_state([self.migrate_from]).apps
        self.original_rows = self.create_legacy_rows(old_apps)

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_to])
        super().tearDown()

    @staticmethod
    def create_legacy_rows(apps):
        User = apps.get_model("accounts", "User")
        Business = apps.get_model("businesses", "Business")
        Product = apps.get_model("catalog", "Product")
        ProductChoice = apps.get_model("catalog", "ProductChoice")

        owner = User.objects.create(
            email="migration-owner@example.com",
            password="unusable",
        )
        other_owner = User.objects.create(
            email="migration-other@example.com",
            password="unusable",
        )
        business = Business.objects.create(owner=owner, name="Seller Studio")
        other_business = Business.objects.create(
            owner=other_owner,
            name="Other Studio",
        )
        product = Product.objects.create(
            business=business,
            name="Trousers",
            description="Migration source.",
        )
        other_product = Product.objects.create(
            business=other_business,
            name="Other trousers",
            description="Other migration source.",
        )
        first = ProductChoice.objects.create(
            business=business,
            product=product,
            size="M",
            color="Black",
            quantity=1,
            is_active=False,
        )
        duplicate = ProductChoice.objects.create(
            business=business,
            product=product,
            size=" m ",
            color=" black ",
            quantity=3,
            is_active=True,
        )
        other = ProductChoice.objects.create(
            business=other_business,
            product=other_product,
            size="M",
            color="Black",
            quantity=7,
            is_active=True,
        )
        return {
            "business_id": business.pk,
            "other_business_id": other_business.pk,
            "first_id": first.pk,
            "duplicate_id": duplicate.pk,
            "other_id": other.pk,
        }

    def test_forward_and_reverse_preserve_choice_rows_and_business_scope(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate([self.migrate_to])
        new_apps = self.executor.loader.project_state([self.migrate_to]).apps
        BusinessSize = new_apps.get_model("catalog", "BusinessSize")
        BusinessColor = new_apps.get_model("catalog", "BusinessColor")
        ProductChoice = new_apps.get_model("catalog", "ProductChoice")

        first = ProductChoice.objects.get(pk=self.original_rows["first_id"])
        duplicate = ProductChoice.objects.get(pk=self.original_rows["duplicate_id"])
        other = ProductChoice.objects.get(pk=self.original_rows["other_id"])

        self.assertEqual(first.size.name, "M")
        self.assertEqual(first.color.name, "Black")
        self.assertEqual(first.size_id, duplicate.size_id)
        self.assertEqual(first.color_id, duplicate.color_id)
        self.assertNotEqual(first.size_id, other.size_id)
        self.assertNotEqual(first.color_id, other.color_id)
        self.assertEqual([first.quantity, duplicate.quantity, other.quantity], [1, 3, 7])
        self.assertEqual(
            [first.is_active, duplicate.is_active, other.is_active],
            [False, True, True],
        )
        self.assertEqual(ProductChoice.objects.count(), 3)
        self.assertEqual(BusinessSize.objects.count(), 2)
        self.assertEqual(BusinessColor.objects.count(), 2)

        self.executor = MigrationExecutor(connection)
        self.executor.migrate([self.migrate_from])
        reverse_apps = self.executor.loader.project_state([self.migrate_from]).apps
        LegacyChoice = reverse_apps.get_model("catalog", "ProductChoice")
        reversed_first = LegacyChoice.objects.get(pk=self.original_rows["first_id"])
        reversed_duplicate = LegacyChoice.objects.get(
            pk=self.original_rows["duplicate_id"]
        )

        self.assertEqual(reversed_first.size, "M")
        self.assertEqual(reversed_first.color, "Black")
        self.assertEqual(reversed_duplicate.size, "M")
        self.assertEqual(reversed_duplicate.color, "Black")
        self.assertEqual(reversed_duplicate.quantity, 3)
        self.assertTrue(reversed_duplicate.is_active)
