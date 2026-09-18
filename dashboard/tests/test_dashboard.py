from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

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
from inventory.models import InventoryAdjustment


class DashboardViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="dashboard-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="dashboard-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Dashboard Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Private Dashboard Studio",
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
        self.url = reverse("shell_home")

    def create_product(self, *, name, business=None, **overrides):
        business = business or self.business
        values = {
            "business": business,
            "name": name,
            "description": f"{name} description",
            "lifecycle": Product.Lifecycle.ACTIVE,
        }
        values.update(overrides)
        return Product.objects.create(**values)

    def create_choice(self, *, product, quantity, is_active=True):
        is_private = product.business_id == self.other_business.pk
        return ProductChoice.objects.create(
            business=product.business,
            product=product,
            size=self.other_size if is_private else self.size,
            color=self.other_color if is_private else self.color,
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

    def build_signal_catalog(self):
        sold_out = self.create_product(name="Sold out coat")
        self.complete_product_truth(sold_out)
        self.create_choice(product=sold_out, quantity=0)

        partial = self.create_product(name="Partial trousers")
        self.complete_product_truth(partial)
        partial_choice = self.create_choice(product=partial, quantity=0)
        self.create_choice(product=partial, quantity=5)

        low_stock = self.create_product(name="Low stock shirt")
        self.complete_product_truth(low_stock)
        low_choice = self.create_choice(product=low_stock, quantity=3)

        missing = self.create_product(name="Missing facts dress")
        self.create_choice(product=missing, quantity=5)

        private = self.create_product(
            name="Private low stock",
            business=self.other_business,
        )
        self.create_choice(product=private, quantity=1)
        return {
            "sold_out": (sold_out, ()),
            "partial_stock": (partial, (partial_choice.pk,)),
            "low_stock": (low_stock, (low_choice.pk,)),
            "missing_information": (missing, ()),
        }

    def test_dashboard_requires_auth_and_matches_business_scoped_attention(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f'{reverse("accounts:login")}?next={self.url}',
        )

        signals = self.build_signal_catalog()
        self.client.force_login(self.owner)
        response = self.client.get(self.url)
        expected = build_seller_attention(business=self.business)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["attention"], expected)
        self.assertContains(response, signals["low_stock"][0].name)
        self.assertNotContains(response, "Private low stock")

    def test_dashboard_uses_georgian_action_language_and_non_color_counts(self):
        self.build_signal_catalog()
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertContains(response, '<html lang="ka">')
        self.assertContains(response, "რას სჭირდება ყურადღება?")
        self.assertContains(response, "აკლია ინფორმაცია")
        self.assertContains(response, "მცირე მარაგი")
        self.assertContains(response, 'aria-label="1 არჩევანი"')

    def test_empty_catalog_quick_add_uses_exact_dashboard_return(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertTrue(response.context["attention"].empty_catalog)
        self.assertContains(response, "დაიწყეთ ერთი პროდუქტით")
        self.assertContains(
            response,
            f'href="{reverse("catalog:product_create")}?next=/"',
        )
        create_response = self.client.get(
            reverse("catalog:product_create"),
            {"next": self.url},
        )
        self.assertEqual(create_response.context["return_url"], self.url)
        self.assertContains(create_response, "მიმოხილვაზე დაბრუნება")

    def test_dashboard_hides_zero_count_cards_behind_one_clear_state(self):
        product = self.create_product(name="Complete stocked product")
        self.complete_product_truth(product)
        self.create_choice(product=product, quantity=5)
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertContains(response, "ამჟამად ყურადღება არაფერს სჭირდება")
        self.assertNotContains(response, 'class="attention-card')

    def test_each_dashboard_signal_drills_into_exact_workspace_membership(self):
        signals = self.build_signal_catalog()
        self.client.force_login(self.owner)
        dashboard = self.client.get(self.url)

        for attention_filter, (expected_product, expected_choice_ids) in signals.items():
            with self.subTest(attention_filter=attention_filter):
                workspace_url = dashboard.context[
                    f"{attention_filter}_workspace_url"
                ]
                response = self.client.get(workspace_url)
                self.assertEqual(
                    [product.pk for product in response.context["products"]],
                    [expected_product.pk],
                )
                self.assertEqual(
                    tuple(response.context["workspace_attention_choice_ids"]),
                    expected_choice_ids,
                )
                self.assertEqual(
                    response.context["workspace_back_to_dashboard_url"],
                    self.url,
                )
                self.assertContains(response, "მიმოხილვაზე დაბრუნება")

    def test_correction_and_stock_paths_preserve_explicit_dashboard_origin(self):
        signals = self.build_signal_catalog()
        low_product, (low_choice_id,) = signals["low_stock"]
        self.client.force_login(self.owner)
        dashboard = self.client.get(self.url)

        missing_url = dashboard.context["missing_information_workspace_url"]
        missing_workspace = self.client.get(missing_url)
        missing_product = signals["missing_information"][0]
        edit_response = self.client.get(
            reverse("catalog:product_edit", args=[missing_product.pk]),
            {"focus": "price", "next": missing_workspace.context["workspace_return_url"]},
        )
        self.assertEqual(
            edit_response.context["return_url"],
            missing_workspace.context["workspace_return_url"],
        )

        low_url = dashboard.context["low_stock_workspace_url"]
        stock_response = self.client.post(
            reverse("inventory:choice_stock_adjust", args=[low_choice_id]),
            {"delta": "1", "response_scope": "workspace", "next": low_url},
        )
        self.assertRedirects(stock_response, low_url)
        self.assertEqual(
            ProductChoice.objects.get(pk=low_choice_id).quantity,
            4,
        )
        self.assertEqual(
            InventoryAdjustment.objects.filter(choice_id=low_choice_id).count(),
            1,
        )
        self.assertEqual(low_product.pk, signals["low_stock"][0].pk)
        self.assertEqual(
            self.client.get(self.url).context["attention"].low_stock_choices.count,
            0,
        )

    def test_invalid_drilldown_and_return_state_fail_closed(self):
        product = self.create_product(name="Must stay hidden")
        self.create_choice(product=product, quantity=1)
        self.client.force_login(self.owner)

        invalid_filter = self.client.get(
            reverse("catalog:product_list"),
            {"attention": "private_state", "origin": "dashboard"},
        )
        repeated_origin = self.client.get(
            f'{reverse("catalog:product_list")}?origin=dashboard&origin=other'
        )
        unsafe_create = self.client.get(
            reverse("catalog:product_create"),
            {"next": "https://example.com/escape"},
        )

        self.assertFalse(invalid_filter.context["workspace_query_is_valid"])
        self.assertNotContains(invalid_filter, product.name)
        self.assertFalse(repeated_origin.context["workspace_query_is_valid"])
        self.assertNotContains(repeated_origin, product.name)
        self.assertEqual(
            unsafe_create.context["return_url"],
            reverse("catalog:product_list"),
        )

    def test_dashboard_query_count_does_not_grow_with_catalog_size(self):
        product = self.create_product(name="First low stock")
        self.create_choice(product=product, quantity=1)
        self.client.force_login(self.owner)
        with CaptureQueriesContext(connection) as initial_queries:
            self.client.get(self.url)

        for index in range(8):
            product = self.create_product(name=f"More low stock {index}")
            self.create_choice(product=product, quantity=1)

        with CaptureQueriesContext(connection) as expanded_queries:
            self.client.get(self.url)

        self.assertEqual(len(expanded_queries), len(initial_queries))

    def test_multiple_businesses_stop_dashboard_without_exposing_data(self):
        Business.objects.create(owner=self.owner, name="Second owned studio")
        product = self.create_product(name="Must not render")
        self.create_choice(product=product, quantity=1)
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 409)
        self.assertContains(
            response,
            "არჩეული იყოს ერთი ბიზნესის სივრცე",
            status_code=409,
        )
        self.assertNotContains(response, product.name, status_code=409)
