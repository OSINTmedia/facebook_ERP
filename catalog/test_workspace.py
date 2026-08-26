from django.contrib.auth import get_user_model
from django.db import connection
from django.http import QueryDict
from django.test import SimpleTestCase, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from businesses.models import Business
from catalog.models import (
    BusinessColor,
    BusinessProductType,
    BusinessSize,
    Product,
    ProductChoice,
)
from catalog.workspace import (
    PRODUCT_DESCRIPTION_EXCERPT_LENGTH,
    ProductWorkspaceState,
    build_product_workspace_cards,
    product_workspace_products,
)
from inventory.models import InventoryAdjustment


class ProductWorkspaceStateTests(SimpleTestCase):
    def test_p6_1_discards_all_unapproved_query_parameters(self):
        state = ProductWorkspaceState.from_query_params(
            QueryDict("q=trousers&next=https%3A%2F%2Fexample.com&unknown=value")
        )

        self.assertEqual(state.query_items, ())
        self.assertEqual(state.return_url, reverse("catalog:product_list"))


class ProductWorkspaceQueryTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="workspace-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="workspace-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )

    def test_query_is_business_scoped_and_deterministically_ordered(self):
        lower_id_same_name = Product.objects.create(
            business=self.business,
            name="Alpha",
            description="Second Alpha product.",
        )
        higher_id_same_name = Product.objects.create(
            business=self.business,
            name="Alpha",
            description="First Alpha product.",
        )
        later_name = Product.objects.create(
            business=self.business,
            name="Beta",
            description="Beta product.",
        )
        Product.objects.create(
            business=self.other_business,
            name="Private",
            description="Other Business product.",
        )

        products = product_workspace_products(business=self.business)

        self.assertEqual(products.query.order_by, ("name", "id"))
        self.assertEqual(
            list(products),
            [lower_id_same_name, higher_id_same_name, later_name],
        )


class ProductCardReadModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="card-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="card-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Card Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Card Studio",
        )
        self.size = BusinessSize.objects.create(
            business=self.business,
            name="M",
        )
        self.color = BusinessColor.objects.create(
            business=self.business,
            name="Black",
        )
        self.other_size = BusinessSize.objects.create(
            business=self.other_business,
            name="Private size",
        )
        self.other_color = BusinessColor.objects.create(
            business=self.other_business,
            name="Private color",
        )

    def create_product(self, *, lifecycle=Product.Lifecycle.ACTIVE, **fields):
        fields.setdefault("name", "Black trousers")
        fields.setdefault("description", "Classic black trousers.")
        return Product.objects.create(
            business=self.business,
            lifecycle=lifecycle,
            **fields,
        )

    def create_choice(self, *, product, quantity=0, is_active=True):
        return ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=self.size,
            color=self.color,
            quantity=quantity,
            is_active=is_active,
        )

    def cards(self):
        products = product_workspace_products(business=self.business)
        return build_product_workspace_cards(
            business=self.business,
            products=products,
        )

    def test_active_positive_card_is_available_with_confirmed_type(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        product = self.create_product(product_type=product_type)
        choice = self.create_choice(product=product, quantity=3)

        card = self.cards()[0]

        self.assertEqual(card.lifecycle_label, "Active")
        self.assertEqual(card.availability_label, "Available")
        self.assertEqual(card.availability_state, "available")
        self.assertEqual(card.product_type_name, "Trousers")
        self.assertEqual(card.active_choice_count, 1)
        self.assertEqual(card.active_stock_total, 3)
        self.assertEqual(card.inactive_choice_count, 0)
        self.assertEqual(card.active_choices[0].choice_id, choice.pk)

    def test_active_card_is_sold_out_when_only_active_choice_is_zero(self):
        product = self.create_product()
        zero_choice = self.create_choice(product=product, quantity=0)
        self.create_choice(product=product, quantity=7, is_active=False)

        card = self.cards()[0]

        self.assertEqual(card.lifecycle_label, "Active")
        self.assertEqual(card.availability_label, "Sold out")
        self.assertEqual(card.availability_state, "sold-out")
        self.assertEqual(card.active_choice_count, 1)
        self.assertEqual(card.active_stock_total, 0)
        self.assertEqual(card.inactive_choice_count, 1)
        self.assertEqual(card.active_choices[0].choice_id, zero_choice.pk)

    def test_draft_with_active_stock_is_not_sellable(self):
        product = self.create_product(lifecycle=Product.Lifecycle.DRAFT)
        self.create_choice(product=product, quantity=4)

        card = self.cards()[0]

        self.assertEqual(card.lifecycle_label, "Draft")
        self.assertEqual(card.availability_label, "Not sellable")
        self.assertEqual(card.availability_state, "not-sellable")
        self.assertEqual(card.active_stock_total, 4)

    def test_duplicate_looking_choices_remain_distinct_card_rows(self):
        product = self.create_product()
        first_choice = self.create_choice(product=product, quantity=1)
        second_choice = self.create_choice(product=product, quantity=2)

        card = self.cards()[0]

        self.assertEqual(card.active_choice_count, 2)
        self.assertEqual(card.active_stock_total, 3)
        self.assertEqual(
            [choice.choice_id for choice in card.active_choices],
            [first_choice.pk, second_choice.pk],
        )

    def test_cross_business_related_facts_are_not_exposed(self):
        other_type = BusinessProductType.objects.create(
            business=self.other_business,
            name="PRIVATE TYPE",
        )
        product = self.create_product()
        Product.objects.filter(pk=product.pk).update(product_type=other_type)
        choice = self.create_choice(product=product, quantity=8)
        ProductChoice.objects.filter(pk=choice.pk).update(
            size=self.other_size,
            color=self.other_color,
        )

        card = self.cards()[0]

        self.assertIsNone(card.product_type_name)
        self.assertEqual(card.active_choices, ())
        self.assertEqual(card.active_stock_total, 0)
        self.assertEqual(card.availability_label, "Sold out")

    def test_description_excerpt_is_bounded_without_inventing_content(self):
        product = self.create_product(description="x" * 200)

        card = self.cards()[0]

        self.assertEqual(
            len(card.description_excerpt),
            PRODUCT_DESCRIPTION_EXCERPT_LENGTH,
        )
        self.assertTrue(card.description_excerpt.endswith("…"))
        self.assertEqual(card.product_id, product.pk)

    def test_card_builder_requires_the_workspace_read_boundary(self):
        product = self.create_product()

        with self.assertRaisesMessage(
            ValueError,
            "Product must come from the Product Workspace query.",
        ):
            build_product_workspace_cards(
                business=self.business,
                products=[product],
            )

    def test_card_query_count_does_not_grow_per_product(self):
        first_product = self.create_product(name="Product 1")
        self.create_choice(product=first_product, quantity=1)

        with CaptureQueriesContext(connection) as one_product_queries:
            first_cards = self.cards()
        self.assertEqual(len(first_cards), 1)

        for index in range(2, 7):
            product = self.create_product(name=f"Product {index}")
            self.create_choice(product=product, quantity=index)

        with CaptureQueriesContext(connection) as many_product_queries:
            many_cards = self.cards()

        self.assertEqual(len(many_cards), 6)
        self.assertEqual(len(one_product_queries), 2)
        self.assertEqual(len(many_product_queries), len(one_product_queries))


class ProductWorkspaceViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="workspace-view-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="workspace-view-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )
        self.url = reverse("catalog:product_list")

    def create_product_with_choice(
        self,
        *,
        name="Workspace trousers",
        quantity=1,
        is_active=True,
    ):
        size, _ = BusinessSize.objects.get_or_create(
            business=self.business,
            name="M",
        )
        color, _ = BusinessColor.objects.get_or_create(
            business=self.business,
            name="Black",
        )
        product = Product.objects.create(
            business=self.business,
            name=name,
            description="Workspace stock controls product.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=size,
            color=color,
            quantity=quantity,
            is_active=is_active,
        )
        return product, choice

    def test_workspace_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_workspace_renders_only_owned_products_in_deterministic_order(self):
        later = Product.objects.create(
            business=self.business,
            name="Zulu",
            description="Later product.",
        )
        first = Product.objects.create(
            business=self.business,
            name="Alpha",
            description="First product.",
        )
        Product.objects.create(
            business=self.other_business,
            name="Private product",
            description="Must not render.",
        )
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_list.html")
        self.assertTemplateUsed(response, "catalog/_product_results.html")
        self.assertEqual(list(response.context["products"]), [first, later])
        self.assertContains(response, first.name)
        self.assertContains(response, later.name)
        self.assertNotContains(response, "Private product")

    def test_workspace_drops_unknown_query_state_from_workflow_links(self):
        product = Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic black trousers.",
        )
        self.client.force_login(self.owner)

        response = self.client.get(
            self.url,
            {
                "q": "trousers",
                "next": "https://example.com/escape",
                "unknown": "value",
            },
        )

        expected_return_url = self.url
        self.assertEqual(
            response.context["workspace_return_url"],
            expected_return_url,
        )
        self.assertContains(
            response,
            f'{reverse("catalog:product_create")}?next={self.url}',
        )
        self.assertContains(
            response,
            f'{reverse("catalog:product_edit", kwargs={"pk": product.pk})}'
            f"?next={self.url}",
        )
        self.assertNotContains(response, "example.com")

    def test_workspace_renders_compact_card_semantics(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        size = BusinessSize.objects.create(business=self.business, name="M")
        color = BusinessColor.objects.create(business=self.business, name="Black")
        product = Product.objects.create(
            business=self.business,
            product_type=product_type,
            name="Black trousers",
            description="Classic black trousers.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=size,
            color=color,
            quantity=3,
        )
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_product_card.html")
        self.assertContains(response, "Lifecycle")
        self.assertContains(response, "Availability")
        self.assertContains(response, "Available")
        self.assertContains(response, "Product type")
        self.assertContains(response, "Trousers")
        self.assertContains(response, f"Choice #{choice.pk}")
        self.assertContains(response, "Size")
        self.assertContains(response, "Color")
        self.assertContains(response, "Quantity")
        self.assertContains(response, 'aria-label="Edit Black trousers"')
        self.assertNotContains(response, "Ready reply")

    def test_workspace_renders_native_stock_controls_only_for_active_choices(self):
        product, active_choice = self.create_product_with_choice(quantity=2)
        inactive_choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=active_choice.size,
            color=active_choice.color,
            quantity=7,
            is_active=False,
        )
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        active_url = reverse(
            "inventory:choice_stock_adjust",
            kwargs={"choice_pk": active_choice.pk},
        )
        inactive_url = reverse(
            "inventory:choice_stock_adjust",
            kwargs={"choice_pk": inactive_choice.pk},
        )
        self.assertContains(
            response,
            f'action="{active_url}"',
            count=1,
        )
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"', count=2)
        self.assertContains(response, f'name="next" value="{self.url}"')
        self.assertContains(response, 'name="delta"', count=2)
        self.assertContains(response, 'value="-1"')
        self.assertContains(response, 'value="1"')
        self.assertContains(
            response,
            f"Decrease stock for Choice #{active_choice.pk}, size M, color Black",
        )
        self.assertContains(
            response,
            f"Increase stock for Choice #{active_choice.pk}, size M, color Black",
        )
        self.assertNotContains(response, f'action="{inactive_url}"')
        self.assertContains(response, "1 inactive")
        self.assertNotContains(response, "hx-post=")

    def test_native_stock_controls_recompute_full_workspace_truth(self):
        product, choice = self.create_product_with_choice(quantity=1)
        adjustment_url = reverse(
            "inventory:choice_stock_adjust",
            kwargs={"choice_pk": choice.pk},
        )
        self.client.force_login(self.owner)

        sold_out_response = self.client.post(
            adjustment_url,
            {"delta": "-1", "next": self.url},
            follow=True,
        )

        self.assertEqual(sold_out_response.redirect_chain, [(self.url, 302)])
        choice.refresh_from_db()
        product.refresh_from_db()
        self.assertEqual(choice.quantity, 0)
        self.assertTrue(choice.is_active)
        self.assertEqual(product.lifecycle, Product.Lifecycle.ACTIVE)
        first_adjustment = InventoryAdjustment.objects.get()
        self.assertEqual(first_adjustment.choice, choice)
        self.assertEqual(first_adjustment.quantity_before, 1)
        self.assertEqual(first_adjustment.quantity_after, 0)
        self.assertEqual(first_adjustment.delta, -1)
        self.assertContains(sold_out_response, "Stock updated to 0.")
        self.assertContains(sold_out_response, "Sold out")
        self.assertContains(sold_out_response, "1 active · 0 total stock")

        available_response = self.client.post(
            adjustment_url,
            {"delta": "1", "next": self.url},
            follow=True,
        )

        choice.refresh_from_db()
        product.refresh_from_db()
        self.assertEqual(choice.quantity, 1)
        self.assertTrue(choice.is_active)
        self.assertEqual(product.lifecycle, Product.Lifecycle.ACTIVE)
        self.assertEqual(InventoryAdjustment.objects.count(), 2)
        latest_adjustment = InventoryAdjustment.objects.latest("created_at")
        self.assertEqual(latest_adjustment.choice, choice)
        self.assertEqual(latest_adjustment.quantity_before, 0)
        self.assertEqual(latest_adjustment.quantity_after, 1)
        self.assertEqual(latest_adjustment.delta, 1)
        self.assertContains(available_response, "Stock updated to 1.")
        self.assertContains(available_response, "Available")
        self.assertContains(available_response, "1 active · 1 total stock")

    def test_native_stock_control_targets_one_duplicate_looking_choice(self):
        product, targeted_choice = self.create_product_with_choice(quantity=1)
        duplicate_choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=targeted_choice.size,
            color=targeted_choice.color,
            quantity=4,
        )
        adjustment_url = reverse(
            "inventory:choice_stock_adjust",
            kwargs={"choice_pk": targeted_choice.pk},
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            adjustment_url,
            {"delta": "1", "next": self.url},
            follow=True,
        )

        targeted_choice.refresh_from_db()
        duplicate_choice.refresh_from_db()
        self.assertEqual(targeted_choice.quantity, 2)
        self.assertEqual(duplicate_choice.quantity, 4)
        adjustment = InventoryAdjustment.objects.get()
        self.assertEqual(adjustment.choice, targeted_choice)
        self.assertContains(response, f"Choice #{targeted_choice.pk}")
        self.assertContains(response, f"Choice #{duplicate_choice.pk}")
        self.assertContains(response, "2 active · 6 total stock")

    def test_native_stock_underflow_returns_authoritative_workspace_error(self):
        product, choice = self.create_product_with_choice(quantity=0)
        adjustment_url = reverse(
            "inventory:choice_stock_adjust",
            kwargs={"choice_pk": choice.pk},
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            adjustment_url,
            {"delta": "-1", "next": self.url},
            follow=True,
        )

        choice.refresh_from_db()
        product.refresh_from_db()
        self.assertEqual(choice.quantity, 0)
        self.assertTrue(choice.is_active)
        self.assertEqual(product.lifecycle, Product.Lifecycle.ACTIVE)
        self.assertFalse(InventoryAdjustment.objects.exists())
        self.assertContains(response, "Choice quantity cannot be negative.")
        self.assertContains(response, "Sold out")
        self.assertContains(response, "1 active · 0 total stock")

    def test_workspace_card_without_active_choices_has_edit_recovery(self):
        product = Product.objects.create(
            business=self.business,
            name="Choice-free draft",
            description="Needs a choice.",
            lifecycle=Product.Lifecycle.DRAFT,
        )
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertContains(response, "No active choices.")
        self.assertContains(response, "Not sellable")
        self.assertContains(
            response,
            f'{reverse("catalog:product_edit", kwargs={"pk": product.pk})}'
            f"?next={self.url}",
            count=1,
        )

    def test_workspace_without_business_is_write_free(self):
        seller_without_business = get_user_model().objects.create_user(
            email="workspace-no-business@example.com",
            password="test-password",
        )
        self.client.force_login(seller_without_business)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No business workspace yet.")
        self.assertFalse(
            Business.objects.filter(owner=seller_without_business).exists()
        )

    def test_workspace_refuses_multiple_businesses(self):
        Business.objects.create(owner=self.owner, name="Second Studio")
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 409)
        self.assertContains(
            response,
            "Multiple business workspaces need an approved switcher",
            status_code=409,
        )

    def test_empty_catalog_has_one_workspace_recovery_action(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_product_results.html")
        self.assertContains(response, "No products yet.")
        self.assertContains(
            response,
            f'{reverse("catalog:product_create")}?next={self.url}',
            count=1,
        )
        self.assertNotContains(response, "Manage product vocabulary")
