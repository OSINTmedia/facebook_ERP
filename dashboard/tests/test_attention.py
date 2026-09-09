from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from businesses.models import Business
from catalog.models import (
    BusinessColor,
    BusinessProductType,
    BusinessSize,
    Product,
    ProductChoice,
    ProductMaterialFact,
)
from dashboard.attention import build_seller_attention


class AttentionQueryServiceTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="attention-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="attention-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Attention Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Attention Studio",
        )
        self.size = BusinessSize.objects.create(business=self.business, name="M")
        self.color = BusinessColor.objects.create(
            business=self.business,
            name="Black",
        )
        self.other_size = BusinessSize.objects.create(
            business=self.other_business,
            name="M",
        )
        self.other_color = BusinessColor.objects.create(
            business=self.other_business,
            name="Black",
        )

    def create_product(self, *, business=None, name, **overrides):
        business = business or self.business
        values = {
            "business": business,
            "name": name,
            "description": f"{name} description",
            "lifecycle": Product.Lifecycle.ACTIVE,
        }
        values.update(overrides)
        return Product.objects.create(**values)

    def create_choice(
        self,
        *,
        product,
        quantity,
        is_active=True,
        business=None,
    ):
        business = business or product.business
        other_business = business == self.other_business
        return ProductChoice.objects.create(
            business=business,
            product=product,
            size=self.other_size if other_business else self.size,
            color=self.other_color if other_business else self.color,
            quantity=quantity,
            is_active=is_active,
        )

    def complete_product_truth(self, product):
        product.product_type = BusinessProductType.objects.create(
            business=product.business,
            name=f"Type {product.pk}",
        )
        product.price = Decimal("50.00")
        product.save(update_fields=["product_type", "price"])
        ProductMaterialFact.objects.create(
            business=product.business,
            product=product,
            canonical_material="Cotton",
            original_text="cotton",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )

    def test_signals_reuse_stock_and_readiness_truth_with_exact_choice_identity(self):
        partial = self.create_product(name="Partial")
        self.complete_product_truth(partial)
        sold_choice = self.create_choice(product=partial, quantity=0)
        stocked_duplicate = self.create_choice(product=partial, quantity=4)

        sold_out = self.create_product(name="Sold out")
        self.create_choice(product=sold_out, quantity=0)

        low_stock = self.create_product(name="Low stock")
        self.create_choice(product=low_stock, quantity=1)

        inactive_only = self.create_product(name="Inactive only")
        self.create_choice(product=inactive_only, quantity=0, is_active=False)

        draft = self.create_product(
            name="Draft",
            lifecycle=Product.Lifecycle.DRAFT,
        )
        self.create_choice(product=draft, quantity=0)

        private = self.create_product(
            business=self.other_business,
            name="Private",
        )
        self.create_choice(
            product=private,
            business=self.other_business,
            quantity=1,
        )

        attention = build_seller_attention(
            business=self.business,
            low_stock_threshold=3,
            list_limit=20,
        )

        self.assertEqual(
            [product.pk for product in attention.sold_out_products.items],
            [sold_out.pk],
        )
        self.assertEqual(attention.sold_out_products.count, 1)
        self.assertEqual(
            [choice.pk for choice in attention.partially_sold_out_choices.items],
            [sold_choice.pk],
        )
        self.assertNotEqual(sold_choice.pk, stocked_duplicate.pk)
        self.assertEqual(
            [choice.product_id for choice in attention.low_stock_choices.items],
            [low_stock.pk],
        )
        self.assertNotIn(
            private.pk,
            [product.pk for product in attention.missing_information_products.items],
        )
        self.assertNotIn(
            partial.pk,
            [product.pk for product in attention.missing_information_products.items],
        )
        self.assertIn(
            inactive_only.pk,
            [product.pk for product in attention.missing_information_products.items],
        )
        self.assertIn(
            draft.pk,
            [product.pk for product in attention.missing_information_products.items],
        )

    @override_settings(DASHBOARD_LOW_STOCK_THRESHOLD=3)
    def test_threshold_boundaries_keep_zero_separate_from_low_stock(self):
        products_by_quantity = {}
        for quantity in (0, 1, 3, 4):
            product = self.create_product(name=f"Quantity {quantity}")
            self.create_choice(product=product, quantity=quantity)
            products_by_quantity[quantity] = product

        attention = build_seller_attention(
            business=self.business,
            list_limit=20,
        )

        self.assertEqual(attention.low_stock_threshold, 3)
        self.assertEqual(
            {choice.quantity for choice in attention.low_stock_choices.items},
            {1, 3},
        )
        self.assertEqual(
            [product.pk for product in attention.sold_out_products.items],
            [products_by_quantity[0].pk],
        )

    def test_lists_are_bounded_while_counts_remain_exact(self):
        for index in range(7):
            product = self.create_product(name=f"Low {index}")
            self.create_choice(product=product, quantity=1)

        attention = build_seller_attention(
            business=self.business,
            low_stock_threshold=1,
            list_limit=2,
        )

        self.assertEqual(attention.low_stock_choices.count, 7)
        self.assertEqual(len(attention.low_stock_choices.items), 2)

    def test_empty_catalog_ignores_archived_lifecycle_and_counts_draft(self):
        self.assertTrue(build_seller_attention(business=self.business).empty_catalog)
        self.create_product(name="Archived", lifecycle="archived")
        self.assertTrue(build_seller_attention(business=self.business).empty_catalog)
        self.create_product(name="Draft", lifecycle=Product.Lifecycle.DRAFT)
        self.assertFalse(build_seller_attention(business=self.business).empty_catalog)

    def test_query_count_is_constant_and_related_choice_truth_is_loaded(self):
        for index in range(12):
            product = self.create_product(name=f"Product {index:02d}")
            self.create_choice(product=product, quantity=index % 4)

        with self.assertNumQueries(2):
            attention = build_seller_attention(
                business=self.business,
                low_stock_threshold=2,
                list_limit=20,
            )
            related_values = [
                (choice.product.name, choice.size.name, choice.color.name)
                for choice in attention.low_stock_choices.items
            ]

        self.assertTrue(related_values)

    def test_invalid_policy_values_are_rejected(self):
        invalid_values = (0, -1, True, 1.5, "3")
        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    build_seller_attention(
                        business=self.business,
                        low_stock_threshold=value,
                    )

        with self.assertRaises(ValueError):
            build_seller_attention(business=self.business, list_limit=-1)

    def test_unsaved_business_is_rejected(self):
        with self.assertRaises(ValueError):
            build_seller_attention(
                business=Business(owner=self.owner, name="Unsaved"),
            )
