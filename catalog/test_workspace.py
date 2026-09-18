from pathlib import Path
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import connection
from django.http import QueryDict
from django.test import SimpleTestCase, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from businesses.models import Business
from catalog.forms import (
    PRODUCT_WORKSPACE_AVAILABILITY_CHOICES,
    PRODUCT_WORKSPACE_LIFECYCLE_CHOICES,
    PRODUCT_WORKSPACE_SEARCH_MAX_LENGTH,
    PRODUCT_WORKSPACE_SEARCH_MAX_TOKENS,
    ProductWorkspaceSearchForm,
)
from catalog.models import (
    BusinessColor,
    BusinessColorAlias,
    BusinessProductType,
    BusinessProductTypeAlias,
    BusinessSize,
    BusinessSizeAlias,
    BusinessTag,
    BusinessTagAlias,
    Product,
    ProductChoice,
    ProductMaterialFact,
    ProductMedia,
    ProductTag,
)
from catalog.workspace import (
    PRODUCT_DESCRIPTION_EXCERPT_LENGTH,
    PRODUCT_WORKSPACE_PAGE_SIZE,
    ProductWorkspaceState,
    build_product_workspace_context,
    build_product_workspace_cards,
    product_workspace_products,
)
from inventory.models import InventoryAdjustment


class ProductWorkspaceStateTests(SimpleTestCase):
    def test_search_state_normalizes_q_and_discards_unapproved_parameters(self):
        state = ProductWorkspaceState.from_query_params(
            QueryDict(
                "q=+black+++trousers+&next=https%3A%2F%2Fexample.com&unknown=value"
            )
        )

        self.assertEqual(state.search_query, "black trousers")
        self.assertEqual(state.query_items, (("q", "black trousers"),))
        self.assertEqual(
            state.return_url,
            f'{reverse("catalog:product_list")}?q=black+trousers',
        )
        self.assertTrue(state.search_is_valid)

    def test_blank_search_is_the_unsearched_workspace(self):
        state = ProductWorkspaceState.from_query_params(QueryDict("q=+++"))

        self.assertEqual(state.search_query, "")
        self.assertEqual(state.query_items, ())
        self.assertEqual(state.return_url, reverse("catalog:product_list"))
        self.assertTrue(state.search_is_valid)

    def test_repeated_search_parameter_is_rejected(self):
        search_form = ProductWorkspaceSearchForm(
            QueryDict("q=trousers&q=private")
        )

        state = ProductWorkspaceState.from_search_form(search_form)

        self.assertFalse(state.search_is_valid)
        self.assertEqual(state.search_query, "")
        self.assertEqual(state.return_url, reverse("catalog:product_list"))
        self.assertEqual(search_form.errors["q"], ["შეიყვანეთ ერთი საძიებო მოთხოვნა."])

    def test_search_length_and_token_limits_are_controlled(self):
        overlong_form = ProductWorkspaceSearchForm(
            {"q": "x" * (PRODUCT_WORKSPACE_SEARCH_MAX_LENGTH + 1)}
        )
        too_many_tokens_form = ProductWorkspaceSearchForm(
            {
                "q": " ".join(
                    f"word{index}"
                    for index in range(PRODUCT_WORKSPACE_SEARCH_MAX_TOKENS + 1)
                )
            }
        )

        self.assertFalse(overlong_form.is_valid())
        self.assertEqual(
            overlong_form.errors["q"],
            ["ძიება მაქსიმუმ 120 სიმბოლოს უნდა შეიცავდეს."],
        )
        self.assertFalse(too_many_tokens_form.is_valid())
        self.assertEqual(
            too_many_tokens_form.errors["q"],
            ["ძიებაში მაქსიმუმ 8 სიტყვა გამოიყენეთ."],
        )

    def test_search_rejects_database_unsafe_control_characters(self):
        search_form = ProductWorkspaceSearchForm({"q": "wool\x01private"})

        self.assertFalse(search_form.is_valid())
        self.assertEqual(
            search_form.errors["q"],
            ["ძიება შეუთავსებელ სიმბოლოებს შეიცავს."],
        )

    def test_filter_state_uses_canonical_order_and_clear_urls(self):
        state = ProductWorkspaceState.from_query_params(
            QueryDict(
                "availability=available&q=+black+++trousers+"
                "&unknown=value&lifecycle=active"
            )
        )

        self.assertTrue(state.is_valid)
        self.assertTrue(state.has_active_filters)
        self.assertEqual(state.lifecycle_filter, Product.Lifecycle.ACTIVE)
        self.assertEqual(state.availability_filter, "available")
        self.assertEqual(
            state.query_items,
            (
                ("q", "black trousers"),
                ("lifecycle", "active"),
                ("availability", "available"),
            ),
        )
        self.assertEqual(
            state.return_url,
            (
                f'{reverse("catalog:product_list")}?q=black+trousers'
                "&lifecycle=active&availability=available"
            ),
        )
        self.assertEqual(
            state.clear_search_url,
            (
                f'{reverse("catalog:product_list")}?lifecycle=active'
                "&availability=available"
            ),
        )
        self.assertEqual(
            state.clear_filters_url,
            f'{reverse("catalog:product_list")}?q=black+trousers',
        )

    def test_repeated_filter_parameters_are_rejected(self):
        search_form = ProductWorkspaceSearchForm(
            QueryDict(
                "q=trousers&lifecycle=active&lifecycle=draft"
                "&availability=available&availability=sold_out"
            )
        )

        state = ProductWorkspaceState.from_search_form(search_form)

        self.assertFalse(state.is_valid)
        self.assertTrue(state.search_is_valid)
        self.assertFalse(state.filters_are_valid)
        self.assertEqual(state.lifecycle_filter, "")
        self.assertEqual(state.availability_filter, "")
        self.assertEqual(
            search_form.errors["lifecycle"],
            ["აირჩიეთ ერთი სტატუსის ფილტრი."],
        )
        self.assertEqual(
            search_form.errors["availability"],
            ["აირჩიეთ ერთი ხელმისაწვდომობის ფილტრი."],
        )
        self.assertEqual(
            state.return_url,
            f'{reverse("catalog:product_list")}?q=trousers',
        )

    def test_filter_fields_expose_only_the_approved_values(self):
        self.assertEqual(
            PRODUCT_WORKSPACE_LIFECYCLE_CHOICES,
            (
                ("", "ყველა სტატუსი"),
                (Product.Lifecycle.ACTIVE, "აქტიური"),
                (Product.Lifecycle.DRAFT, "მონახაზი"),
                (Product.Lifecycle.ARCHIVED, "დაარქივებული"),
            ),
        )
        self.assertEqual(
            PRODUCT_WORKSPACE_AVAILABILITY_CHOICES,
            (
                ("", "ყველა ხელმისაწვდომობა"),
                ("available", "მარაგშია"),
                ("sold_out", "ამოიწურა"),
            ),
        )
        search_form = ProductWorkspaceSearchForm(
            {"lifecycle": "hidden", "availability": "low_stock"}
        )

        self.assertFalse(search_form.is_valid())
        self.assertIn("აირჩიეთ დასაშვები მნიშვნელობა", search_form.errors["lifecycle"][0])
        self.assertIn(
            "აირჩიეთ დასაშვები მნიშვნელობა",
            search_form.errors["availability"][0],
        )

    def test_return_url_state_accepts_only_exact_canonical_workspace_urls(self):
        state = ProductWorkspaceState.from_return_url(
            f'{reverse("catalog:product_list")}?q=black+trousers'
            "&lifecycle=active&availability=available"
        )

        self.assertEqual(state.search_query, "black trousers")
        self.assertEqual(state.lifecycle_filter, Product.Lifecycle.ACTIVE)
        self.assertEqual(state.availability_filter, "available")

        invalid_urls = (
            "https://example.com/products/",
            f'{reverse("catalog:product_list")}?unknown=value',
            f'{reverse("catalog:product_list")}?q=trousers&q=private',
            f'{reverse("catalog:product_list")}?q=+trousers+%20',
            f'{reverse("catalog:product_list")}#stock',
        )
        for invalid_url in invalid_urls:
            with self.subTest(invalid_url=invalid_url):
                with self.assertRaises(ValueError):
                    ProductWorkspaceState.from_return_url(invalid_url)

    def test_workspace_context_exposes_one_canonical_state_contract(self):
        state = ProductWorkspaceState.from_query_params(
            QueryDict("q=trousers&lifecycle=active")
        )

        context = build_product_workspace_context(
            state=state,
            business=None,
        )

        self.assertEqual(context["workspace_search_query"], "trousers")
        self.assertEqual(context["workspace_lifecycle_filter"], "active")
        self.assertEqual(
            context["workspace_return_url"],
            f'{reverse("catalog:product_list")}?q=trousers&lifecycle=active',
        )
        self.assertEqual(context["product_cards"], ())
        self.assertFalse(context["catalog_has_products"])


class ProductWorkspaceAttentionDrilldownTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="attention-workspace@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="attention-workspace-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Attention Workspace",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Private Attention Workspace",
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
        self.url = reverse("catalog:product_list")

    def create_product(self, *, name, business=None, complete=True):
        business = business or self.business
        product = Product.objects.create(
            business=business,
            name=name,
            description=f"{name} description",
            lifecycle=Product.Lifecycle.ACTIVE,
            price=Decimal("50.00") if complete else None,
        )
        if complete:
            product.product_type = BusinessProductType.objects.create(
                business=business,
                name=f"Type {product.pk}",
            )
            product.save(update_fields=["product_type"])
            ProductMaterialFact.objects.create(
                business=business,
                product=product,
                canonical_material="Cotton",
                original_text="cotton",
                source=ProductMaterialFact.Source.DESCRIPTION,
            )
        return product

    def create_choice(self, *, product, quantity):
        is_private = product.business_id == self.other_business.pk
        return ProductChoice.objects.create(
            business=product.business,
            product=product,
            size=self.other_size if is_private else self.size,
            color=self.other_color if is_private else self.color,
            quantity=quantity,
        )

    def test_attention_state_is_canonical_visible_and_clearable(self):
        state = ProductWorkspaceState.from_query_params(
            QueryDict(
                "origin=dashboard&attention=low_stock&q=shirt&lifecycle=active"
            )
        )

        self.assertTrue(state.is_valid)
        self.assertEqual(state.attention_filter, "low_stock")
        self.assertTrue(state.has_dashboard_origin)
        self.assertEqual(state.active_filter_count, 2)
        self.assertEqual(
            state.return_url,
            f"{self.url}?q=shirt&lifecycle=active&attention=low_stock&origin=dashboard",
        )
        self.assertEqual(
            state.clear_filters_url,
            f"{self.url}?q=shirt&origin=dashboard",
        )
        self.assertEqual(
            state.clear_all_url,
            f"{self.url}?origin=dashboard",
        )
        self.assertEqual(
            ProductWorkspaceState.from_return_url(state.return_url),
            state,
        )

    def test_attention_drilldowns_use_exact_business_scoped_membership(self):
        low = self.create_product(name="Low product")
        low_choice = self.create_choice(product=low, quantity=1)
        stocked_choice = self.create_choice(product=low, quantity=5)
        other = self.create_product(name="Other product")
        self.create_choice(product=other, quantity=5)
        private = self.create_product(
            name="Private product",
            business=self.other_business,
        )
        self.create_choice(product=private, quantity=1)
        self.client.force_login(self.owner)

        response = self.client.get(
            self.url,
            {"attention": "low_stock", "origin": "dashboard"},
        )

        self.assertEqual([product.pk for product in response.context["products"]], [low.pk])
        self.assertEqual(
            tuple(response.context["workspace_attention_choice_ids"]),
            (low_choice.pk,),
        )
        card = response.context["product_cards"][0]
        self.assertEqual(
            [choice.choice_id for choice in card.active_choices if choice.is_attention_target],
            [low_choice.pk],
        )
        self.assertFalse(
            next(
                choice for choice in card.active_choices
                if choice.choice_id == stocked_choice.pk
            ).is_attention_target
        )
        self.assertContains(response, "საყურადღებო — მცირე მარაგი")
        self.assertContains(response, "საყურადღებო არჩევანი", count=1)
        self.assertNotContains(response, private.name)

    def test_unknown_or_repeated_attention_context_fails_closed(self):
        product = self.create_product(name="Do not widen")
        self.create_choice(product=product, quantity=1)
        self.client.force_login(self.owner)

        unknown = self.client.get(self.url, {"attention": "unknown"})
        repeated = self.client.get(
            f"{self.url}?attention=low_stock&attention=sold_out"
        )
        repeated_origin = self.client.get(
            f"{self.url}?origin=dashboard&origin=other"
        )

        for response in (unknown, repeated, repeated_origin):
            with self.subTest(query=response.request["QUERY_STRING"]):
                self.assertFalse(response.context["workspace_query_is_valid"])
                self.assertNotContains(response, product.name)

    def test_attention_drilldown_query_count_does_not_grow_with_catalog_size(self):
        product = self.create_product(name="First low product")
        self.create_choice(product=product, quantity=1)
        self.client.force_login(self.owner)
        drilldown = {"attention": "low_stock", "origin": "dashboard"}
        with CaptureQueriesContext(connection) as initial_queries:
            self.client.get(self.url, drilldown)

        for index in range(8):
            product = self.create_product(name=f"More low product {index}")
            self.create_choice(product=product, quantity=1)

        with CaptureQueriesContext(connection) as expanded_queries:
            self.client.get(self.url, drilldown)

        self.assertEqual(len(expanded_queries), len(initial_queries))

    def test_htmx_stock_refresh_removes_resolved_low_stock_membership(self):
        product = self.create_product(name="Threshold product")
        choice = self.create_choice(product=product, quantity=3)
        self.client.force_login(self.owner)
        return_url = f"{self.url}?attention=low_stock&origin=dashboard"

        response = self.client.post(
            reverse(
                "inventory:choice_stock_adjust",
                kwargs={"choice_pk": choice.pk},
            ),
            {
                "delta": "1",
                "next": return_url,
                "response_scope": "workspace",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_product_results.html")
        self.assertContains(response, "მარაგი განახლდა: 4.")
        self.assertContains(response, "<strong>0</strong> პროდუქტი")
        self.assertNotContains(response, product.name)
        choice.refresh_from_db()
        self.assertEqual(choice.quantity, 4)
        self.assertEqual(InventoryAdjustment.objects.filter(choice=choice).count(), 1)


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

    def create_filter_product(
        self,
        *,
        name,
        lifecycle=Product.Lifecycle.ACTIVE,
        quantity=None,
        choice_is_active=True,
    ):
        product = Product.objects.create(
            business=self.business,
            name=name,
            description=f"{name} description.",
            lifecycle=lifecycle,
        )
        if quantity is not None:
            size, _ = BusinessSize.objects.get_or_create(
                business=self.business,
                name="M",
            )
            color, _ = BusinessColor.objects.get_or_create(
                business=self.business,
                name="Black",
            )
            ProductChoice.objects.create(
                business=self.business,
                product=product,
                size=size,
                color=color,
                quantity=quantity,
                is_active=choice_is_active,
            )
        return product

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

    def test_search_matches_each_approved_persisted_field_and_alias(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        BusinessProductTypeAlias.objects.create(
            business=self.business,
            product_type=product_type,
            alias="Slacks",
        )
        tag = BusinessTag.objects.create(
            business=self.business,
            name="Formal",
        )
        BusinessTagAlias.objects.create(
            business=self.business,
            tag=tag,
            alias="Officewear",
        )
        size = BusinessSize.objects.create(business=self.business, name="Medium")
        BusinessSizeAlias.objects.create(
            business=self.business,
            size=size,
            alias="M",
        )
        color = BusinessColor.objects.create(
            business=self.business,
            name="Midnight blue",
        )
        BusinessColorAlias.objects.create(
            business=self.business,
            color=color,
            alias="Navy",
        )
        product = Product.objects.create(
            business=self.business,
            product_type=product_type,
            name="City pants",
            description="A tailored wardrobe staple.",
        )
        ProductTag.objects.create(
            business=self.business,
            product=product,
            tag=tag,
        )
        ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=size,
            color=color,
        )
        ProductMaterialFact.objects.create(
            business=self.business,
            product=product,
            canonical_material="Wool",
            original_text="Merino blend",
            source=ProductMaterialFact.Source.MANUAL,
        )

        for query in (
            "city",
            "tailored",
            "trousers",
            "slacks",
            "formal",
            "officewear",
            "medium",
            "m",
            "midnight",
            "navy",
            "wool",
            "merino",
        ):
            with self.subTest(query=query):
                matches = product_workspace_products(
                    business=self.business,
                    search_query=query,
                )
                self.assertEqual(list(matches), [product])

    def test_search_uses_and_across_tokens_without_duplicate_products(self):
        tag = BusinessTag.objects.create(
            business=self.business,
            name="Formal",
        )
        product = Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Tailored wool trousers.",
        )
        ProductTag.objects.create(
            business=self.business,
            product=product,
            tag=tag,
        )
        second_tag = BusinessTag.objects.create(
            business=self.business,
            name="Black tie",
        )
        ProductTag.objects.create(
            business=self.business,
            product=product,
            tag=second_tag,
        )
        Product.objects.create(
            business=self.business,
            name="Black shirt",
            description="Casual cotton.",
        )

        matches = product_workspace_products(
            business=self.business,
            search_query="black formal",
        )

        self.assertEqual(list(matches), [product])

    def test_search_matches_canonical_related_values_without_alias_rows(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Jacket",
        )
        tag = BusinessTag.objects.create(
            business=self.business,
            name="Outerwear",
        )
        size = BusinessSize.objects.create(business=self.business, name="Large")
        color = BusinessColor.objects.create(
            business=self.business,
            name="Burgundy",
        )
        product = Product.objects.create(
            business=self.business,
            product_type=product_type,
            name="Structured product",
            description="Canonical relation coverage.",
        )
        ProductTag.objects.create(
            business=self.business,
            product=product,
            tag=tag,
        )
        ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=size,
            color=color,
        )

        for query in ("jacket", "outerwear", "large", "burgundy"):
            with self.subTest(query=query):
                matches = product_workspace_products(
                    business=self.business,
                    search_query=query,
                )
                self.assertEqual(list(matches), [product])

    def test_search_does_not_match_other_business_facts_or_aliases(self):
        owned_product = Product.objects.create(
            business=self.business,
            name="Owned product",
            description="Visible wording.",
        )
        other_type = BusinessProductType.objects.create(
            business=self.other_business,
            name="Private type",
        )
        BusinessProductTypeAlias.objects.create(
            business=self.other_business,
            product_type=other_type,
            alias="Private alias",
        )
        Product.objects.create(
            business=self.other_business,
            product_type=other_type,
            name="Private product",
            description="Private description.",
        )
        Product.objects.filter(pk=owned_product.pk).update(product_type=other_type)
        local_tag = BusinessTag.objects.create(
            business=self.business,
            name="Local tag",
        )
        other_tag = BusinessTag.objects.create(
            business=self.other_business,
            name="Private tag",
        )
        BusinessTagAlias.objects.create(
            business=self.other_business,
            tag=other_tag,
            alias="Private tag alias",
        )
        tag_link = ProductTag.objects.create(
            business=self.business,
            product=owned_product,
            tag=local_tag,
        )
        ProductTag.objects.filter(pk=tag_link.pk).update(
            business=self.other_business,
            tag=other_tag,
        )
        local_size = BusinessSize.objects.create(
            business=self.business,
            name="Local size",
        )
        local_color = BusinessColor.objects.create(
            business=self.business,
            name="Local color",
        )
        other_size = BusinessSize.objects.create(
            business=self.other_business,
            name="Private size",
        )
        BusinessSizeAlias.objects.create(
            business=self.other_business,
            size=other_size,
            alias="Private size alias",
        )
        other_color = BusinessColor.objects.create(
            business=self.other_business,
            name="Private color",
        )
        BusinessColorAlias.objects.create(
            business=self.other_business,
            color=other_color,
            alias="Private color alias",
        )
        choice = ProductChoice.objects.create(
            business=self.business,
            product=owned_product,
            size=local_size,
            color=local_color,
        )
        ProductChoice.objects.filter(pk=choice.pk).update(
            color=other_color,
        )
        material = ProductMaterialFact.objects.create(
            business=self.business,
            product=owned_product,
            canonical_material="Local material",
            original_text="Local wording",
            source=ProductMaterialFact.Source.MANUAL,
        )
        ProductMaterialFact.objects.filter(pk=material.pk).update(
            business=self.other_business,
            canonical_material="Private material",
            original_text="Private material wording",
        )

        matches = product_workspace_products(
            business=self.business,
            search_query="private",
        )
        partial_choice_matches = product_workspace_products(
            business=self.business,
            search_query="local size",
        )

        self.assertEqual(list(matches), [])
        self.assertEqual(list(partial_choice_matches), [])

    def test_search_card_query_count_does_not_grow_per_product(self):
        first_product = Product.objects.create(
            business=self.business,
            name="Match 1",
            description="Searchable collection.",
        )

        with CaptureQueriesContext(connection) as one_product_queries:
            first_cards = build_product_workspace_cards(
                business=self.business,
                products=product_workspace_products(
                    business=self.business,
                    search_query="searchable",
                ),
            )
        self.assertEqual(len(first_cards), 1)

        for index in range(2, 7):
            Product.objects.create(
                business=self.business,
                name=f"Match {index}",
                description="Searchable collection.",
            )

        with CaptureQueriesContext(connection) as many_product_queries:
            many_cards = build_product_workspace_cards(
                business=self.business,
                products=product_workspace_products(
                    business=self.business,
                    search_query="searchable",
                ),
            )

        self.assertEqual(len(many_cards), 6)
        self.assertEqual(len(one_product_queries), 2)
        self.assertEqual(len(many_product_queries), len(one_product_queries))

    def test_lifecycle_and_computed_availability_filters_are_distinct(self):
        available = self.create_filter_product(
            name="Active available",
            quantity=2,
        )
        sold_out = self.create_filter_product(
            name="Active sold out",
            quantity=0,
        )
        inactive_stock = self.create_filter_product(
            name="Active inactive stock",
            quantity=5,
            choice_is_active=False,
        )
        draft_with_stock = self.create_filter_product(
            name="Draft with stock",
            lifecycle=Product.Lifecycle.DRAFT,
            quantity=7,
        )

        active_products = product_workspace_products(
            business=self.business,
            lifecycle_filter=Product.Lifecycle.ACTIVE,
        )
        draft_products = product_workspace_products(
            business=self.business,
            lifecycle_filter=Product.Lifecycle.DRAFT,
        )
        available_products = product_workspace_products(
            business=self.business,
            availability_filter="available",
        )
        sold_out_products = product_workspace_products(
            business=self.business,
            availability_filter="sold_out",
        )

        self.assertEqual(
            list(active_products),
            [available, inactive_stock, sold_out],
        )
        self.assertEqual(list(draft_products), [draft_with_stock])
        self.assertEqual(list(available_products), [available])
        self.assertEqual(
            list(sold_out_products),
            [inactive_stock, sold_out],
        )
        self.assertNotIn(draft_with_stock, sold_out_products)

    def test_search_and_filters_compose_with_and_semantics(self):
        matching = self.create_filter_product(
            name="Black active trousers",
            quantity=1,
        )
        self.create_filter_product(name="Black sold-out trousers", quantity=0)
        self.create_filter_product(name="Blue active shirt", quantity=1)

        products = product_workspace_products(
            business=self.business,
            search_query="black trousers",
            lifecycle_filter=Product.Lifecycle.ACTIVE,
            availability_filter="available",
        )

        self.assertEqual(list(products), [matching])

    def test_availability_filter_rejects_cross_business_choice_stock(self):
        local_product = self.create_filter_product(
            name="Local sold out",
            quantity=0,
        )
        corrupt_vocabulary_product = self.create_filter_product(
            name="Local product with corrupt vocabulary",
            quantity=4,
        )
        other_size = BusinessSize.objects.create(
            business=self.other_business,
            name="Private size",
        )
        other_color = BusinessColor.objects.create(
            business=self.other_business,
            name="Private color",
        )
        other_product = Product.objects.create(
            business=self.other_business,
            name="Private product",
            description="Private product.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        other_choice = ProductChoice.objects.create(
            business=self.other_business,
            product=other_product,
            size=other_size,
            color=other_color,
            quantity=9,
        )
        ProductChoice.objects.filter(pk=other_choice.pk).update(
            product=local_product
        )
        ProductChoice.objects.filter(
            product=corrupt_vocabulary_product
        ).update(
            size=other_size,
            color=other_color,
        )

        available_products = product_workspace_products(
            business=self.business,
            availability_filter="available",
        )
        sold_out_products = product_workspace_products(
            business=self.business,
            availability_filter="sold_out",
        )

        self.assertEqual(list(available_products), [])
        self.assertEqual(
            list(sold_out_products),
            [corrupt_vocabulary_product, local_product],
        )

    def test_query_boundary_rejects_unsupported_filter_values(self):
        with self.assertRaisesMessage(
            ValueError,
            "Unsupported Product lifecycle filter.",
        ):
            product_workspace_products(
                business=self.business,
                lifecycle_filter="hidden",
            )
        with self.assertRaisesMessage(
            ValueError,
            "Unsupported Product availability filter.",
        ):
            product_workspace_products(
                business=self.business,
                availability_filter="low_stock",
            )

    def test_availability_filter_card_query_count_does_not_grow_per_product(self):
        self.create_filter_product(name="Available 1", quantity=1)

        with CaptureQueriesContext(connection) as one_product_queries:
            first_cards = build_product_workspace_cards(
                business=self.business,
                products=product_workspace_products(
                    business=self.business,
                    availability_filter="available",
                ),
            )

        for index in range(2, 7):
            self.create_filter_product(
                name=f"Available {index}",
                quantity=index,
            )

        with CaptureQueriesContext(connection) as many_product_queries:
            many_cards = build_product_workspace_cards(
                business=self.business,
                products=product_workspace_products(
                    business=self.business,
                    availability_filter="available",
                ),
            )

        self.assertEqual(len(first_cards), 1)
        self.assertEqual(len(many_cards), 6)
        self.assertEqual(len(one_product_queries), 2)
        self.assertEqual(len(many_product_queries), len(one_product_queries))


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

        self.assertEqual(card.lifecycle_label, "აქტიური")
        self.assertIsNone(card.price)
        self.assertEqual(card.currency, "GEL")
        self.assertIsNone(card.primary_media_id)
        self.assertEqual(card.availability_label, "მარაგშია")
        self.assertEqual(card.availability_state, "available")
        self.assertEqual(card.product_type_name, "Trousers")
        self.assertEqual(card.active_choice_count, 1)
        self.assertEqual(card.active_stock_total, 3)
        self.assertEqual(card.inactive_choice_count, 0)
        self.assertEqual(card.active_choices[0].choice_id, choice.pk)

    def test_card_exposes_complete_buyer_answer_coverage(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        product = self.create_product(
            product_type=product_type,
            price=Decimal("49.90"),
        )
        self.create_choice(product=product, quantity=3)
        ProductMaterialFact.objects.create(
            business=self.business,
            product=product,
            canonical_material="Cotton",
            original_text="cotton",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )

        card = self.cards()[0]

        self.assertEqual(
            card.answerable_question_labels,
            ("ფასი", "მარაგი", "ზომა და ფერი", "პროდუქტის ტიპი", "მასალა"),
        )
        self.assertEqual(card.missing_question_labels, ())
        self.assertIsNone(card.readiness_correction_label)
        self.assertIsNone(card.readiness_correction_target)
        self.assertIsNone(card.readiness_correction_fragment)
        self.assertFalse(card.is_partially_sold_out)

    def test_card_exposes_smallest_missing_truth_correction(self):
        product = self.create_product()
        self.create_choice(product=product, quantity=1)

        card = self.cards()[0]

        self.assertEqual(
            card.answerable_question_labels,
            ("მარაგი", "ზომა და ფერი"),
        )
        self.assertEqual(
            card.missing_question_labels,
            ("ფასი", "პროდუქტის ტიპი", "მასალა"),
        )
        self.assertEqual(card.readiness_correction_label, "ფასის დამატება")
        self.assertEqual(card.readiness_correction_target, "price")
        self.assertEqual(card.readiness_correction_fragment, "#id_price")

    def test_partial_sold_out_uses_only_mixed_active_choice_stock(self):
        product = self.create_product()
        zero_choice = self.create_choice(product=product, quantity=0)
        positive_choice = self.create_choice(product=product, quantity=2)
        self.create_choice(product=product, quantity=0, is_active=False)

        card = self.cards()[0]

        self.assertTrue(card.is_partially_sold_out)
        self.assertEqual(
            [choice.choice_id for choice in card.active_choices],
            [zero_choice.pk, positive_choice.pk],
        )
        zero_choice.quantity = 1
        zero_choice.save(update_fields=["quantity", "updated_at"])

        refreshed_card = self.cards()[0]

        self.assertFalse(refreshed_card.is_partially_sold_out)

    def test_card_exposes_confirmed_price_with_business_currency(self):
        self.business.default_currency = "USD"
        self.business.save(update_fields=["default_currency", "updated_at"])
        self.create_product(price=Decimal("49.90"))

        card = self.cards()[0]

        self.assertEqual(card.price, Decimal("49.90"))
        self.assertEqual(card.currency, "USD")

    def test_card_exposes_only_business_scoped_primary_media_identity(self):
        product = self.create_product()
        media = ProductMedia.objects.bulk_create(
            [
                ProductMedia(
                    business=self.business,
                    product=product,
                    image=(
                        f"products/{self.business.pk}/{product.pk}/"
                        f"{'a' * 32}.png"
                    ),
                )
            ]
        )[0]

        card = self.cards()[0]

        self.assertEqual(card.primary_media_id, media.pk)

    def test_card_hides_cross_business_media_even_from_corrupt_related_state(self):
        product = self.create_product()
        ProductMedia.objects.bulk_create(
            [
                ProductMedia(
                    business=self.other_business,
                    product=product,
                    image=(
                        f"products/{self.other_business.pk}/{product.pk}/"
                        f"{'b' * 32}.png"
                    ),
                )
            ]
        )

        card = self.cards()[0]

        self.assertIsNone(card.primary_media_id)

    def test_active_card_is_sold_out_when_only_active_choice_is_zero(self):
        product = self.create_product()
        zero_choice = self.create_choice(product=product, quantity=0)
        self.create_choice(product=product, quantity=7, is_active=False)

        card = self.cards()[0]

        self.assertEqual(card.lifecycle_label, "აქტიური")
        self.assertEqual(card.availability_label, "ამოიწურა")
        self.assertEqual(card.availability_state, "sold-out")
        self.assertEqual(card.active_choice_count, 1)
        self.assertEqual(card.active_stock_total, 0)
        self.assertEqual(card.inactive_choice_count, 1)
        self.assertEqual(card.active_choices[0].choice_id, zero_choice.pk)
        self.assertFalse(card.is_partially_sold_out)

    def test_draft_with_active_stock_is_not_sellable(self):
        product = self.create_product(lifecycle=Product.Lifecycle.DRAFT)
        self.create_choice(product=product, quantity=4)

        card = self.cards()[0]

        self.assertEqual(card.lifecycle_label, "მონახაზი")
        self.assertEqual(card.availability_label, "ამჟამად არ იყიდება")
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
        material = ProductMaterialFact.objects.create(
            business=self.business,
            product=product,
            canonical_material="PRIVATE MATERIAL",
            original_text="private material",
            source=ProductMaterialFact.Source.MANUAL,
        )
        Product.objects.filter(pk=product.pk).update(product_type=other_type)
        ProductMaterialFact.objects.filter(pk=material.pk).update(
            business=self.other_business
        )
        choice = self.create_choice(product=product, quantity=8)
        ProductChoice.objects.filter(pk=choice.pk).update(
            size=self.other_size,
            color=self.other_color,
        )

        card = self.cards()[0]

        self.assertIsNone(card.product_type_name)
        self.assertEqual(card.active_choices, ())
        self.assertEqual(card.active_stock_total, 0)
        self.assertEqual(card.availability_label, "ამოიწურა")
        self.assertNotIn("მასალა", card.answerable_question_labels)
        self.assertIn("მასალა", card.missing_question_labels)

    def test_description_excerpt_is_bounded_without_inventing_content(self):
        product = self.create_product(description="x" * 200)

        card = self.cards()[0]

        self.assertEqual(
            len(card.description_excerpt),
            PRODUCT_DESCRIPTION_EXCERPT_LENGTH,
        )
        self.assertTrue(card.description_excerpt.endswith("…"))
        self.assertEqual(card.product_id, product.pk)

    def test_description_derived_identity_has_no_repeated_excerpt(self):
        descriptions = (
            "Description-first   black\ntrousers",
            "long " * 50,
        )
        for description in descriptions:
            with self.subTest(description=description):
                name = " ".join(description.split())[:160]
                product = self.create_product(name=name, description=description)

                card = next(
                    card for card in self.cards() if card.product_id == product.pk
                )

                self.assertEqual(card.description_excerpt, "")

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


class _ProductWorkspacePaginationFixture:
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email=f"{self.__class__.__name__}@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email=f"other-{self.__class__.__name__}@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Paginated Seller",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Paginated Seller",
        )
        self.size = BusinessSize.objects.create(
            business=self.business,
            name="M",
        )
        self.color = BusinessColor.objects.create(
            business=self.business,
            name="Black",
        )
        self.url = reverse("catalog:product_list")
        self.client.force_login(self.owner)

    def create_product(
        self,
        *,
        name,
        lifecycle=Product.Lifecycle.DRAFT,
        quantity=None,
    ):
        product = Product.objects.create(
            business=self.business,
            name=name,
            description=f"{name} description.",
            lifecycle=lifecycle,
        )
        choice = None
        if quantity is not None:
            choice = ProductChoice.objects.create(
                business=self.business,
                product=product,
                size=self.size,
                color=self.color,
                quantity=quantity,
            )
        return product, choice

    def create_catalog(
        self,
        count,
        *,
        prefix="Product",
        lifecycle=Product.Lifecycle.DRAFT,
        quantity=None,
    ):
        return [
            self.create_product(
                name=f"{prefix} {index:02d}",
                lifecycle=lifecycle,
                quantity=quantity,
            )
            for index in range(count)
        ]


class ProductWorkspacePaginationTests(
    _ProductWorkspacePaginationFixture,
    TestCase,
):
    def test_first_and_next_pages_are_bounded_with_stable_ordering(self):
        products = self.create_catalog(PRODUCT_WORKSPACE_PAGE_SIZE + 1)
        Product.objects.create(
            business=self.other_business,
            name="Private Product",
            description="Must remain private.",
        )

        first_response = self.client.get(self.url)
        next_response = self.client.get(self.url, {"page": 2})

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(
            list(first_response.context["products"]),
            [product for product, _ in products[:PRODUCT_WORKSPACE_PAGE_SIZE]],
        )
        self.assertEqual(
            list(next_response.context["products"]),
            [products[-1][0]],
        )
        self.assertEqual(
            first_response.context["workspace_result_count"],
            PRODUCT_WORKSPACE_PAGE_SIZE + 1,
        )
        self.assertEqual(first_response.context["workspace_page_count"], 2)
        self.assertContains(first_response, "გვერდი 1 / 2")
        self.assertContains(first_response, 'href="/products/?page=2"')
        self.assertNotContains(first_response, "Private Product")

    def test_duplicate_ordering_keys_use_product_identity_as_tie_breaker(self):
        products = [
            self.create_product(name="Same name")[0]
            for _ in range(PRODUCT_WORKSPACE_PAGE_SIZE + 1)
        ]

        first_response = self.client.get(self.url)
        next_response = self.client.get(self.url, {"page": 2})

        rendered_ids = [
            product.pk for product in first_response.context["products"]
        ] + [product.pk for product in next_response.context["products"]]
        self.assertEqual(rendered_ids, [product.pk for product in products])

    def test_search_filter_and_page_links_use_one_canonical_state(self):
        self.create_catalog(
            PRODUCT_WORKSPACE_PAGE_SIZE + 1,
            prefix="Match",
        )

        response = self.client.get(
            self.url,
            {"q": "  match ", "lifecycle": "draft", "page": 2},
        )

        canonical_url = f"{self.url}?q=match&lifecycle=draft&page=2"
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["workspace_return_url"], canonical_url)
        self.assertEqual(
            response.context["workspace_previous_page_url"],
            f"{self.url}?q=match&lifecycle=draft",
        )
        self.assertContains(response, "გვერდი 2 / 2")
        self.assertContains(
            response,
            'name="next" value="/products/?q=match&amp;lifecycle=draft&amp;page=2"',
        )
        self.assertEqual(len(response.context["product_cards"]), 1)

    def test_malformed_and_out_of_range_pages_redirect_to_canonical_state(self):
        self.create_catalog(PRODUCT_WORKSPACE_PAGE_SIZE + 1)

        malformed = self.client.get(self.url, {"page": "invalid"})
        repeated = self.client.get(f"{self.url}?page=2&page=3")
        first_page_alias = self.client.get(self.url, {"page": 1})
        leading_zero = self.client.get(self.url, {"page": "0002"})
        out_of_range = self.client.get(self.url, {"page": 999})

        self.assertRedirects(malformed, self.url, fetch_redirect_response=False)
        self.assertRedirects(repeated, self.url, fetch_redirect_response=False)
        self.assertRedirects(first_page_alias, self.url, fetch_redirect_response=False)
        self.assertRedirects(
            leading_zero,
            f"{self.url}?page=2",
            fetch_redirect_response=False,
        )
        self.assertRedirects(
            out_of_range,
            f"{self.url}?page=2",
            fetch_redirect_response=False,
        )

    def test_empty_catalog_page_request_recovers_to_empty_first_page(self):
        response = self.client.get(self.url, {"page": 2}, follow=True)

        self.assertEqual(response.redirect_chain, [(self.url, 302)])
        self.assertEqual(response.context["workspace_result_count"], 0)
        self.assertContains(response, "პროდუქტები ჯერ არ არის.")

    def test_workspace_query_count_does_not_grow_with_page_contents(self):
        self.create_product(name="Product 00")
        with CaptureQueriesContext(connection) as one_product_queries:
            one_product_response = self.client.get(self.url)

        self.create_catalog(PRODUCT_WORKSPACE_PAGE_SIZE - 1, prefix="More")
        with CaptureQueriesContext(connection) as full_page_queries:
            full_page_response = self.client.get(self.url)

        self.assertEqual(len(one_product_response.context["product_cards"]), 1)
        self.assertEqual(
            len(full_page_response.context["product_cards"]),
            PRODUCT_WORKSPACE_PAGE_SIZE,
        )
        self.assertEqual(len(full_page_queries), len(one_product_queries))


class ProductWorkspacePaginationJourneyTests(
    _ProductWorkspacePaginationFixture,
    TestCase,
):
    def test_page_context_reaches_edit_correction_and_add_similar(self):
        products = self.create_catalog(PRODUCT_WORKSPACE_PAGE_SIZE + 1)
        source = products[-1][0]
        response = self.client.get(self.url, {"page": 2})

        template_encoded_return = "/products/%3Fpage%3D2"
        self.assertContains(response, f"next={template_encoded_return}")
        self.assertContains(
            response,
            f'action="{reverse("catalog:product_add_similar", args=[source.pk])}"',
        )

        similar_response = self.client.post(
            reverse("catalog:product_add_similar", args=[source.pk]),
            {"next": f"{self.url}?page=2"},
        )

        self.assertEqual(similar_response.status_code, 302)
        self.assertIn(
            "next=%2Fproducts%2F%3Fpage%3D2",
            similar_response["Location"],
        )

    def test_stock_membership_change_recovers_empty_last_page_for_htmx(self):
        products = self.create_catalog(
            PRODUCT_WORKSPACE_PAGE_SIZE + 1,
            prefix="მარაგშია",
            lifecycle=Product.Lifecycle.ACTIVE,
            quantity=1,
        )
        target_product, target_choice = products[-1]
        workspace_url = f"{self.url}?availability=available&page=2"

        response = self.client.post(
            reverse(
                "inventory:choice_stock_adjust",
                kwargs={"choice_pk": target_choice.pk},
            ),
            {
                "delta": "-1",
                "next": workspace_url,
                "response_scope": "workspace",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["HX-Replace-Url"],
            f"{self.url}?availability=available",
        )
        self.assertEqual(response.context["workspace_page_number"], 1)
        self.assertEqual(response.context["workspace_result_count"], 12)
        self.assertNotContains(response, target_product.name)
        self.assertContains(response, "მიმდინარე შედეგებიდან გადავიდა")

    def test_dashboard_drilldown_preserves_origin_across_pages(self):
        self.create_catalog(
            PRODUCT_WORKSPACE_PAGE_SIZE + 1,
            prefix="Needs information",
        )

        response = self.client.get(
            self.url,
            {
                "attention": "missing_information",
                "origin": "dashboard",
                "page": 2,
            },
        )

        expected_previous = (
            f"{self.url}?attention=missing_information&origin=dashboard"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["workspace_previous_page_url"],
            expected_previous,
        )
        self.assertEqual(
            response.context["workspace_back_to_dashboard_url"],
            reverse("shell_home"),
        )

    def test_archive_and_restore_recover_a_page_emptied_by_membership_change(self):
        active_products = self.create_catalog(
            PRODUCT_WORKSPACE_PAGE_SIZE + 1,
            prefix="აქტიური",
            lifecycle=Product.Lifecycle.ACTIVE,
            quantity=1,
        )
        archived_product = active_products[-1][0]

        archive_response = self.client.post(
            reverse("catalog:product_archive", args=[archived_product.pk]),
            {"next": f"{self.url}?page=2"},
            follow=True,
        )

        self.assertEqual(
            archive_response.redirect_chain,
            [(f"{self.url}?page=2", 302), (self.url, 302)],
        )
        archived_product.refresh_from_db()
        self.assertEqual(archived_product.lifecycle, Product.Lifecycle.ARCHIVED)

        self.create_catalog(
            PRODUCT_WORKSPACE_PAGE_SIZE,
            prefix="დაარქივებული",
            lifecycle=Product.Lifecycle.ARCHIVED,
        )
        archived_url = f"{self.url}?lifecycle=archived&page=2"
        restore_response = self.client.post(
            reverse("catalog:product_restore", args=[archived_product.pk]),
            {"next": archived_url},
            follow=True,
        )

        canonical_archived_url = f"{self.url}?lifecycle=archived"
        self.assertEqual(
            restore_response.redirect_chain,
            [(archived_url, 302), (canonical_archived_url, 302)],
        )
        archived_product.refresh_from_db()
        self.assertEqual(archived_product.lifecycle, Product.Lifecycle.DRAFT)


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
        lifecycle=Product.Lifecycle.ACTIVE,
        price=None,
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
            lifecycle=lifecycle,
            price=price,
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

    def test_final_seller_experience_uses_georgian_and_recovery_hooks(self):
        product, _choice = self.create_product_with_choice(
            name="ძალიან გრძელი ქართული პროდუქტის სახელი",
        )
        self.client.force_login(self.owner)

        workspace_response = self.client.get(self.url)
        create_response = self.client.get(reverse("catalog:product_create"))

        self.assertContains(workspace_response, '<html lang="ka">')
        self.assertContains(workspace_response, "პროდუქტები")
        self.assertContains(workspace_response, "მზა პასუხი")
        self.assertContains(workspace_response, "სურათი არ არის")
        self.assertContains(
            workspace_response,
            f'aria-label="{product.name} — სურათი არ არის"',
        )
        self.assertNotContains(workspace_response, ">Account</span>")
        self.assertContains(create_response, 'id="product-form-transport-error"')
        self.assertContains(create_response, "გვერდის განახლება")
        self.assertContains(create_response, "js/product_workspace.js")

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

    def test_workspace_prioritizes_daily_actions_before_secondary_settings(self):
        self.create_product_with_choice(name="Daily stock product")
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        content = response.content.decode()
        add_product = (
            f'href="{reverse("catalog:product_create")}?next={self.url}"'
        )
        search = 'class="product-workspace-search"'
        product_card = 'class="product-card"'
        vocabulary = (
            f'href="{reverse("catalog:choice_vocabulary")}?next={self.url}"'
        )
        self.assertContains(response, add_product, count=1)
        self.assertContains(response, vocabulary, count=1)
        self.assertContains(response, "<strong>1</strong> პროდუქტი")
        self.assertLess(content.index(add_product), content.index(search))
        self.assertLess(content.index(search), content.index(product_card))
        self.assertLess(content.index(product_card), content.index(vocabulary))

    def test_workspace_preserves_q_and_drops_unknown_workflow_state(self):
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

        expected_return_url = f"{self.url}?q=trousers"
        self.assertEqual(
            response.context["workspace_return_url"],
            expected_return_url,
        )
        self.assertEqual(response.context["workspace_search_query"], "trousers")
        self.assertContains(response, "q%3Dtrousers")
        self.assertNotContains(response, "example.com")
        self.assertNotContains(response, "unknown")

    def test_workspace_search_filters_and_shows_applied_query_count(self):
        matching_product, _ = self.create_product_with_choice(
            name="Black trousers",
        )
        Product.objects.create(
            business=self.business,
            name="Blue shirt",
            description="Different product.",
        )
        self.client.force_login(self.owner)

        response = self.client.get(self.url, {"q": "  black   trousers "})

        expected_return_url = f"{self.url}?q=black+trousers"
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["products"]), [matching_product])
        self.assertEqual(
            response.context["workspace_return_url"],
            expected_return_url,
        )
        self.assertEqual(response.context["workspace_result_count"], 1)
        self.assertContains(response, "პროდუქტი „black trousers“ ძიებისთვის")
        self.assertContains(response, "Black trousers")
        self.assertNotContains(response, "Blue shirt")
        self.assertContains(response, "q%3Dblack%2Btrousers")
        self.assertContains(
            response,
            f'name="next" value="{expected_return_url}"',
        )
        self.assertContains(response, "ძიების გასუფთავება", count=1)

    def test_workspace_search_no_result_has_one_clear_recovery(self):
        Product.objects.create(
            business=self.business,
            name="Black trousers",
            description="Classic product.",
        )
        self.client.force_login(self.owner)

        response = self.client.get(self.url, {"q": "missing"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["workspace_result_count"], 0)
        self.assertContains(response, "პროდუქტი „missing“ ძიებისთვის")
        self.assertContains(response, "ძიებას „missing“ არცერთი პროდუქტი არ ემთხვევა.")
        self.assertContains(response, "სცადეთ უფრო მარტივი ძიება.")
        self.assertContains(response, "ძიების გასუფთავება", count=1)
        self.assertNotContains(response, "პროდუქტები ჯერ არ არის.")
        self.assertNotContains(
            response,
            f'href="{reverse("catalog:product_create")}?next=',
        )

    def test_search_on_an_empty_catalog_keeps_the_catalog_empty_state(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url, {"q": "missing"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["workspace_result_count"], 0)
        self.assertContains(response, "პროდუქტი „missing“ ძიებისთვის")
        self.assertContains(response, "პროდუქტები ჯერ არ არის.")
        self.assertNotContains(response, "No products match")
        self.assertContains(
            response,
            f'href="{reverse("catalog:product_create")}?next=',
            count=1,
        )
        self.assertContains(response, "ძიების გასუფთავება", count=1)

    def test_invalid_repeated_search_is_controlled_and_does_not_list_products(self):
        Product.objects.create(
            business=self.business,
            name="Private if unfiltered",
            description="Must not render for invalid search.",
        )
        self.client.force_login(self.owner)

        response = self.client.get(f"{self.url}?q=first&q=second")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["workspace_search_is_valid"])
        self.assertContains(response, "შეიყვანეთ ერთი საძიებო მოთხოვნა.")
        self.assertContains(response, "ძიება არ გამოყენებულა.")
        self.assertNotContains(response, "Private if unfiltered")

    def test_workspace_filters_render_canonical_state_and_clear_actions(self):
        matching_product, _ = self.create_product_with_choice(
            name="Black available trousers",
            quantity=2,
        )
        self.create_product_with_choice(
            name="Black sold-out trousers",
            quantity=0,
        )
        self.create_product_with_choice(
            name="Black draft trousers",
            quantity=4,
            lifecycle=Product.Lifecycle.DRAFT,
        )
        self.client.force_login(self.owner)

        response = self.client.get(
            self.url,
            {
                "availability": "available",
                "q": "  black   trousers ",
                "lifecycle": "active",
                "unknown": "discard-me",
            },
        )

        expected_return_url = (
            f"{self.url}?q=black+trousers"
            "&lifecycle=active&availability=available"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["products"]), [matching_product])
        self.assertEqual(
            response.context["workspace_return_url"],
            expected_return_url,
        )
        self.assertEqual(
            response.context["workspace_clear_search_url"],
            f"{self.url}?lifecycle=active&availability=available",
        )
        self.assertEqual(
            response.context["workspace_clear_filters_url"],
            f"{self.url}?q=black+trousers",
        )
        self.assertContains(response, "აქტიური: 2")
        self.assertContains(response, "სტატუსი — აქტიური")
        self.assertContains(response, "ხელმისაწვდომობა — მარაგშია")
        self.assertContains(response, 'class="product-workspace-state-summary"')
        self.assertNotContains(
            response,
            'class="product-workspace-filters" open',
        )
        self.assertContains(response, "ძიების გასუფთავება", count=1)
        self.assertContains(response, "ფილტრების გასუფთავება", count=1)
        self.assertContains(response, "ყველას გასუფთავება", count=1)
        self.assertContains(
            response,
            f'name="next" value="{expected_return_url.replace("&", "&amp;")}"',
        )
        self.assertNotContains(response, "discard-me")

    def test_workspace_filter_empty_states_have_one_matching_recovery(self):
        self.create_product_with_choice(
            name="Only available product",
            quantity=1,
        )
        self.client.force_login(self.owner)

        filter_response = self.client.get(
            self.url,
            {"availability": "sold_out"},
        )
        combined_response = self.client.get(
            self.url,
            {"q": "missing", "availability": "available"},
        )

        self.assertContains(
            filter_response,
            "აქტიურ ფილტრებს არცერთი პროდუქტი არ ემთხვევა.",
        )
        self.assertContains(filter_response, "<strong>0</strong> პროდუქტი ·")
        self.assertContains(filter_response, "ფილტრების გასუფთავება", count=1)
        self.assertNotContains(filter_response, "ყველას გასუფთავება")
        self.assertNotContains(filter_response, "პროდუქტები ჯერ არ არის.")
        self.assertContains(
            combined_response,
            "ამ ძიებასა და ფილტრებს არცერთი პროდუქტი არ ემთხვევა.",
        )
        self.assertContains(combined_response, "ყველას გასუფთავება", count=1)
        self.assertNotContains(combined_response, "ფილტრების გასუფთავება")
        self.assertNotContains(combined_response, "ძიების გასუფთავება")

    def test_invalid_filter_is_controlled_and_does_not_list_products(self):
        Product.objects.create(
            business=self.business,
            name="Must not render unfiltered",
            description="Invalid filters cannot widen the query.",
        )
        self.client.force_login(self.owner)

        unknown_response = self.client.get(
            self.url,
            {"availability": "low_stock"},
        )
        repeated_response = self.client.get(
            f"{self.url}?lifecycle=active&lifecycle=draft"
        )

        self.assertFalse(unknown_response.context["workspace_query_is_valid"])
        self.assertContains(unknown_response, "აირჩიეთ დასაშვები მნიშვნელობა")
        self.assertContains(unknown_response, "ფილტრები არ გამოყენებულა.")
        self.assertContains(
            unknown_response,
            'class="product-workspace-filters" open',
        )
        self.assertNotContains(unknown_response, "Must not render unfiltered")
        self.assertFalse(repeated_response.context["workspace_query_is_valid"])
        self.assertContains(
            repeated_response,
            "აირჩიეთ ერთი სტატუსის ფილტრი.",
        )
        self.assertNotContains(repeated_response, "Must not render unfiltered")

    def test_workspace_validation_errors_expose_accessibility_hooks(self):
        self.client.force_login(self.owner)

        search_response = self.client.get(f"{self.url}?q=one&q=two")
        filter_response = self.client.get(
            self.url,
            {"availability": "low_stock"},
        )

        self.assertContains(
            search_response,
            'data-workspace-helptext-for="id_q"',
        )
        self.assertContains(search_response, 'id="id_q_errors"')
        self.assertContains(
            search_response,
            'data-workspace-error-for="id_q"',
        )
        self.assertContains(filter_response, 'id="id_availability_errors"')
        self.assertContains(
            filter_response,
            'data-workspace-error-for="id_availability"',
        )

    def test_workspace_accessibility_script_and_styles_cover_feedback_contract(self):
        project_root = Path(__file__).resolve().parents[1]
        workspace_script = (
            project_root / "static" / "js" / "product_workspace.js"
        ).read_text()
        workspace_styles = (
            project_root / "static" / "css" / "app.css"
        ).read_text()

        self.assertIn("syncWorkspaceFormAccessibility", workspace_script)
        self.assertIn("syncFieldErrors", workspace_script)
        self.assertIn("showProductFormTransportRecovery", workspace_script)
        self.assertIn('field.setAttribute("aria-describedby", describedBy)', workspace_script)
        self.assertIn('field.setAttribute("aria-errormessage", errorId)', workspace_script)
        self.assertIn("setWorkspaceActionBusy", workspace_script)
        self.assertIn('form.setAttribute("aria-busy", String(isBusy))', workspace_script)
        self.assertIn("button.disabled = true", workspace_script)
        self.assertIn("button.disabled = false", workspace_script)
        self.assertIn('button.setAttribute("aria-disabled", "true")', workspace_script)
        self.assertIn("readyReplyControl", workspace_script)
        self.assertIn('trigger?.setAttribute("aria-expanded", "true")', workspace_script)
        self.assertIn("readyReplySlot(control)?.replaceChildren()", workspace_script)
        self.assertIn("if (!panel)", workspace_script)
        self.assertIn("navigator.clipboard?.writeText", workspace_script)
        self.assertIn("copyText.select()", workspace_script)
        self.assertIn("closeReadyReply(panel)", workspace_script)
        self.assertIn(".product-workspace :is(", workspace_styles)
        self.assertIn(".product-workspace .button[aria-disabled=\"true\"]", workspace_styles)
        self.assertIn("min-height: 2.75rem", workspace_styles)

    def test_true_empty_catalog_remains_distinct_with_active_filters(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            self.url,
            {"q": "missing", "availability": "sold_out"},
        )

        self.assertContains(response, "პროდუქტები ჯერ არ არის.")
        self.assertNotContains(response, "No products match")
        self.assertContains(response, "პროდუქტის დამატება", count=2)
        self.assertContains(response, "ყველას გასუფთავება", count=1)

    def test_native_stock_fallback_updates_availability_filter_membership(self):
        product, choice = self.create_product_with_choice(
            name="ხელმისაწვდომობა transition",
            quantity=1,
        )
        adjustment_url = reverse(
            "inventory:choice_stock_adjust",
            kwargs={"choice_pk": choice.pk},
        )
        available_url = f"{self.url}?availability=available"
        sold_out_url = f"{self.url}?availability=sold_out"
        self.client.force_login(self.owner)

        sold_out_response = self.client.post(
            adjustment_url,
            {
                "delta": "-1",
                "next": available_url,
                "response_scope": "workspace",
            },
            follow=True,
        )

        self.assertEqual(sold_out_response.redirect_chain, [(available_url, 302)])
        self.assertEqual(list(sold_out_response.context["products"]), [])
        self.assertContains(
            sold_out_response,
            "აქტიურ ფილტრებს არცერთი პროდუქტი არ ემთხვევა.",
        )
        choice.refresh_from_db()
        self.assertEqual(choice.quantity, 0)

        available_response = self.client.post(
            adjustment_url,
            {
                "delta": "1",
                "next": sold_out_url,
                "response_scope": "workspace",
            },
            follow=True,
        )

        self.assertEqual(available_response.redirect_chain, [(sold_out_url, 302)])
        self.assertEqual(list(available_response.context["products"]), [])
        self.assertContains(
            available_response,
            "აქტიურ ფილტრებს არცერთი პროდუქტი არ ემთხვევა.",
        )
        choice.refresh_from_db()
        self.assertEqual(choice.quantity, 1)
        self.assertEqual(InventoryAdjustment.objects.filter(choice=choice).count(), 2)
        self.assertEqual(product.lifecycle, Product.Lifecycle.ACTIVE)

    def test_native_stock_fallback_preserves_searched_workspace(self):
        product, choice = self.create_product_with_choice(
            name="Searchable trousers",
            quantity=1,
        )
        adjustment_url = reverse(
            "inventory:choice_stock_adjust",
            kwargs={"choice_pk": choice.pk},
        )
        searched_workspace_url = f"{self.url}?q=searchable"
        self.client.force_login(self.owner)

        response = self.client.post(
            adjustment_url,
            {
                "delta": "1",
                "next": searched_workspace_url,
                "response_scope": "workspace",
            },
            follow=True,
        )

        self.assertEqual(
            response.redirect_chain,
            [(searched_workspace_url, 302)],
        )
        self.assertEqual(response.context["workspace_search_query"], "searchable")
        self.assertEqual(list(response.context["products"]), [product])
        choice.refresh_from_db()
        self.assertEqual(choice.quantity, 2)
        self.assertContains(response, "აქტიური: 1 · სულ მარაგი: 2")

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
            price=Decimal("49.90"),
        )
        choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=size,
            color=color,
            quantity=3,
        )
        ProductMaterialFact.objects.create(
            business=self.business,
            product=product,
            canonical_material="Cotton",
            original_text="cotton",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_product_card.html")
        self.assertContains(response, "სტატუსი")
        self.assertContains(response, "ფასი")
        self.assertContains(response, "49.90 GEL")
        self.assertContains(response, "ხელმისაწვდომობა")
        self.assertContains(response, "მარაგშია")
        self.assertContains(response, "პროდუქტის ტიპი")
        self.assertContains(response, "Trousers")
        self.assertContains(response, "საჭირო პასუხები მზადაა")
        self.assertContains(
            response,
            "მზადაა:</strong> ფასი, მარაგი, ზომა და ფერი, პროდუქტის ტიპი, მასალა",
        )
        self.assertContains(response, f"არჩევანი #{choice.pk}")
        self.assertContains(response, "ზომა")
        self.assertContains(response, "ფერი")
        self.assertContains(response, "რაოდენობა")
        self.assertContains(
            response,
            (
                f'aria-label="მიმდინარე რაოდენობა: არჩევანი #{choice.pk}, '
                'ზომა M, ფერი Black"'
            ),
        )
        self.assertContains(response, 'aria-label="Black trousers — რედაქტირება"')
        self.assertContains(response, "მზა პასუხი")
        self.assertContains(response, "data-ready-reply-trigger")
        self.assertNotContains(response, "data-ready-reply-panel")
        rendered = response.content.decode()
        card_markup = rendered[rendered.index('<article class="product-card"') :]
        self.assertLess(
            card_markup.index("ფასი"),
            card_markup.index("სტატუსი"),
        )
        self.assertLess(
            card_markup.index("სტატუსი"),
            card_markup.index(product.description),
        )

    def test_ready_reply_panel_requires_authentication_and_business_ownership(self):
        owned_product, _choice = self.create_product_with_choice()
        foreign_product = Product.objects.create(
            business=self.other_business,
            name="Private reply product",
            description="Private reply truth.",
        )
        owned_url = reverse(
            "catalog:product_ready_reply",
            kwargs={"pk": owned_product.pk},
        )
        foreign_url = reverse(
            "catalog:product_ready_reply",
            kwargs={"pk": foreign_product.pk},
        )

        anonymous_response = self.client.get(owned_url)

        self.assertRedirects(
            anonymous_response,
            f"{reverse('accounts:login')}?next={owned_url}",
        )

        self.client.force_login(self.owner)
        foreign_response = self.client.get(foreign_url)

        self.assertEqual(foreign_response.status_code, 404)
        self.assertNotContains(
            foreign_response,
            "Private reply truth.",
            status_code=404,
        )

    def test_ready_reply_panel_separates_copy_text_notes_and_safe_return(self):
        product, _choice = self.create_product_with_choice(
            name="Incomplete reply product",
        )
        panel_url = reverse(
            "catalog:product_ready_reply",
            kwargs={"pk": product.pk},
        )
        return_url = f"{self.url}?q=workspace&lifecycle=active"
        self.client.force_login(self.owner)

        response = self.client.get(panel_url, {"next": return_url})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_ready_reply_panel.html")
        self.assertEqual(response.headers["Cache-Control"], "private, no-store")
        self.assertContains(response, "data-ready-reply-panel")
        self.assertContains(response, "data-ready-reply-text")
        self.assertContains(response, "data-ready-reply-copy")
        self.assertContains(response, "გაგზავნამდე")
        self.assertContains(response, "ფასი აკლია")
        self.assertContains(
            response,
            (
                "focus=price&amp;next=%2Fproducts%2F%3Fq%3Dworkspace"
                "%26lifecycle%3Dactive#id_price"
            ),
        )

        rendered = response.content.decode()
        copy_start = rendered.index("<textarea")
        copy_end = rendered.index("</textarea>", copy_start)
        copy_markup = rendered[copy_start:copy_end]
        for note in response.context["ready_reply"].seller_notes:
            self.assertNotIn(note.text, copy_markup)

    def test_ready_reply_panel_renders_complete_partial_and_sold_out_truth(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        product, stocked_choice = self.create_product_with_choice(
            name="Reply states",
            quantity=2,
            price=Decimal("49.90"),
        )
        product.product_type = product_type
        product.save(update_fields=["product_type", "updated_at"])
        ProductMaterialFact.objects.create(
            business=self.business,
            product=product,
            canonical_material="Cotton",
            original_text="cotton",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )
        panel_url = reverse(
            "catalog:product_ready_reply",
            kwargs={"pk": product.pk},
        )
        self.client.force_login(self.owner)

        complete_response = self.client.get(panel_url, {"next": self.url})

        self.assertContains(
            complete_response,
            "ხელმისაწვდომობა: მარაგშია.",
        )
        self.assertNotContains(complete_response, "გაგზავნამდე")

        size_l = BusinessSize.objects.create(
            business=self.business,
            name="L",
        )
        ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=size_l,
            color=stocked_choice.color,
            quantity=0,
        )

        partial_response = self.client.get(panel_url, {"next": self.url})

        self.assertContains(
            partial_response,
            "ხელმისაწვდომობა: მარაგშია, თუმცა ზოგი არჩევანი ამოწურულია.",
        )

        stocked_choice.quantity = 0
        stocked_choice.save(update_fields=["quantity", "updated_at"])

        sold_out_response = self.client.get(panel_url, {"next": self.url})

        self.assertContains(
            sold_out_response,
            "ხელმისაწვდომობა: ამოწურულია.",
        )

    def test_workspace_missing_price_is_explicit_and_never_free(self):
        self.create_product_with_choice(name="Missing price product")
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertContains(response, "ფასი")
        self.assertContains(response, "აკლია")
        self.assertNotContains(response, "Free")

    def test_workspace_renders_readiness_with_exact_correction_return(self):
        self.create_product_with_choice(name="Workspace readiness")
        self.client.force_login(self.owner)
        workspace_state = {
            "q": "workspace",
            "lifecycle": "active",
            "availability": "available",
        }

        response = self.client.get(self.url, workspace_state)

        self.assertContains(response, "პასუხები მომხმარებლისთვის")
        self.assertContains(response, "მზადაა:</strong> მარაგი, ზომა და ფერი")
        self.assertContains(
            response,
            "აკლია:</strong> ფასი, პროდუქტის ტიპი, მასალა",
        )
        self.assertContains(response, "ფასის დამატება")
        self.assertContains(response, "?focus=price&amp;next=")
        self.assertContains(
            response,
            "q%3Dworkspace%26lifecycle%3Dactive%26availability%3Davailable",
        )
        self.assertContains(response, "#id_price")
        self.assertNotContains(response, "completion")
        self.assertNotContains(response, "% ready")

    def test_workspace_material_correction_opens_target_and_keeps_return(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        product, _choice = self.create_product_with_choice(
            name="Material correction",
            price=Decimal("49.90"),
        )
        product.product_type = product_type
        product.save(update_fields=["product_type", "updated_at"])
        return_url = f"{self.url}?q=material"
        self.client.force_login(self.owner)

        workspace_response = self.client.get(self.url, {"q": "material"})

        self.assertContains(workspace_response, "აკლია:</strong> მასალა")
        self.assertContains(workspace_response, "მასალის დადასტურება")
        self.assertContains(workspace_response, "focus=materials")
        self.assertContains(workspace_response, "#material-section")

        edit_response = self.client.get(
            reverse("catalog:product_edit", kwargs={"pk": product.pk}),
            {"focus": "materials", "next": return_url},
        )

        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(edit_response.context["return_url"], return_url)
        self.assertEqual(edit_response.context["correction_target"], "materials")
        self.assertTrue(edit_response.context["material_section_open"])
        self.assertContains(edit_response, 'id="material-section"')

    def test_workspace_does_not_repeat_description_derived_identity(self):
        product, _choice = self.create_product_with_choice(
            name="Description-first trousers",
        )
        product.description = "Description-first   trousers"
        product.save(update_fields=["description", "updated_at"])
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertContains(
            response,
            f'<h2 id="product-card-title-{product.pk}">{product.name}</h2>',
            count=1,
            html=True,
        )
        self.assertNotContains(response, 'class="product-card__description"')

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
            count=2,
        )
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"', count=5)
        self.assertContains(response, f'name="next" value="{self.url}"')
        self.assertContains(response, 'name="delta"', count=2)
        self.assertContains(response, 'value="-1"')
        self.assertContains(response, 'value="1"')
        self.assertContains(
            response,
            'name="response_scope" value="workspace"',
        )
        self.assertContains(response, f'hx-post="{active_url}"', count=3)
        self.assertContains(
            response,
            'hx-target="#product-workspace-results"',
            count=3,
        )
        self.assertContains(response, 'hx-swap="outerHTML"', count=3)
        self.assertContains(
            response,
            'hx-sync="#product-workspace-results:drop"',
            count=3,
        )
        self.assertContains(response, "js/product_workspace.js")
        self.assertContains(response, "შედეგების განახლება")
        self.assertContains(
            response,
            f"მარაგის შემცირება: არჩევანი #{active_choice.pk}, ზომა M, ფერი Black",
        )
        self.assertContains(
            response,
            f"მარაგის გაზრდა: არჩევანი #{active_choice.pk}, ზომა M, ფერი Black",
        )
        self.assertContains(
            response,
            f"ზუსტი მარაგის მითითება: არჩევანი #{active_choice.pk}, ზომა M, ფერი Black",
        )
        self.assertContains(response, 'name="quantity"', count=1)
        self.assertNotContains(response, f'action="{inactive_url}"')
        self.assertContains(response, "არააქტიური: 1")

    def test_native_stock_controls_recompute_full_workspace_truth(self):
        product, choice = self.create_product_with_choice(quantity=1)
        adjustment_url = reverse(
            "inventory:choice_stock_adjust",
            kwargs={"choice_pk": choice.pk},
        )
        self.client.force_login(self.owner)

        sold_out_response = self.client.post(
            adjustment_url,
            {
                "delta": "-1",
                "next": self.url,
                "response_scope": "workspace",
            },
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
        self.assertContains(sold_out_response, "მარაგი განახლდა: 0.")
        self.assertContains(sold_out_response, "ამოიწურა")
        self.assertContains(sold_out_response, "აქტიური: 1 · სულ მარაგი: 0")

        available_response = self.client.post(
            adjustment_url,
            {
                "delta": "1",
                "next": self.url,
                "response_scope": "workspace",
            },
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
        self.assertContains(available_response, "მარაგი განახლდა: 1.")
        self.assertContains(available_response, "მარაგშია")
        self.assertContains(available_response, "აქტიური: 1 · სულ მარაგი: 1")

    def test_workspace_htmx_refreshes_partial_stock_readiness_signal(self):
        product, targeted_choice = self.create_product_with_choice(quantity=1)
        other_choice = ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=targeted_choice.size,
            color=targeted_choice.color,
            quantity=1,
        )
        adjustment_url = reverse(
            "inventory:choice_stock_adjust",
            kwargs={"choice_pk": targeted_choice.pk},
        )
        self.client.force_login(self.owner)

        partial_response = self.client.post(
            adjustment_url,
            {
                "delta": "-1",
                "next": self.url,
                "response_scope": "workspace",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(partial_response.status_code, 200)
        self.assertTemplateUsed(partial_response, "catalog/_product_results.html")
        self.assertContains(partial_response, "ზოგი არჩევანი ამოიწურა")
        self.assertContains(partial_response, "მზადაა:</strong> მარაგი, ზომა და ფერი")
        targeted_choice.refresh_from_db()
        other_choice.refresh_from_db()
        self.assertEqual(targeted_choice.quantity, 0)
        self.assertEqual(other_choice.quantity, 1)

        restored_response = self.client.post(
            adjustment_url,
            {
                "delta": "1",
                "next": self.url,
                "response_scope": "workspace",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(restored_response.status_code, 200)
        self.assertNotContains(restored_response, "ზოგი არჩევანი ამოიწურა")
        targeted_choice.refresh_from_db()
        other_choice.refresh_from_db()
        self.assertEqual(targeted_choice.quantity, 1)
        self.assertEqual(other_choice.quantity, 1)
        self.assertEqual(InventoryAdjustment.objects.count(), 2)

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
            {
                "delta": "1",
                "next": self.url,
                "response_scope": "workspace",
            },
            follow=True,
        )

        targeted_choice.refresh_from_db()
        duplicate_choice.refresh_from_db()
        self.assertEqual(targeted_choice.quantity, 2)
        self.assertEqual(duplicate_choice.quantity, 4)
        adjustment = InventoryAdjustment.objects.get()
        self.assertEqual(adjustment.choice, targeted_choice)
        self.assertContains(response, f"არჩევანი #{targeted_choice.pk}")
        self.assertContains(response, f"არჩევანი #{duplicate_choice.pk}")
        self.assertContains(response, "აქტიური: 2 · სულ მარაგი: 6")

    def test_native_stock_underflow_returns_authoritative_workspace_error(self):
        product, choice = self.create_product_with_choice(quantity=0)
        adjustment_url = reverse(
            "inventory:choice_stock_adjust",
            kwargs={"choice_pk": choice.pk},
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            adjustment_url,
            {
                "delta": "-1",
                "next": self.url,
                "response_scope": "workspace",
            },
            follow=True,
        )

        choice.refresh_from_db()
        product.refresh_from_db()
        self.assertEqual(choice.quantity, 0)
        self.assertTrue(choice.is_active)
        self.assertEqual(product.lifecycle, Product.Lifecycle.ACTIVE)
        self.assertFalse(InventoryAdjustment.objects.exists())
        self.assertContains(response, "მარაგი ნულზე ნაკლები ვერ იქნება.")
        self.assertContains(response, "ამოიწურა")
        self.assertContains(response, "აქტიური: 1 · სულ მარაგი: 0")

    def test_workspace_card_without_active_choices_has_edit_recovery(self):
        product = Product.objects.create(
            business=self.business,
            name="Choice-free draft",
            description="Needs a choice.",
            lifecycle=Product.Lifecycle.DRAFT,
        )
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertContains(response, "აქტიური არჩევანი არ არის.")
        self.assertContains(response, "ამჟამად არ იყიდება")
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
        self.assertContains(response, "ბიზნესის სივრცე ჯერ არ არის.")
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
            "პროდუქტების სანახავად უნდა არჩეული იყოს ერთი ბიზნესის სივრცე",
            status_code=409,
        )

    def test_empty_catalog_has_one_workspace_recovery_action(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/_product_results.html")
        self.assertContains(response, "პროდუქტები ჯერ არ არის.")
        self.assertContains(
            response,
            f'{reverse("catalog:product_create")}?next={self.url}',
            count=1,
        )
        self.assertNotContains(response, "პროდუქტის სიტყვარის მართვა")


class ProductWorkspaceDirectSetTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="workspace-direct-set@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="workspace-direct-set-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Workspace Direct Set Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Workspace Direct Set Studio",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="Workspace direct set trousers",
            description="Workspace direct set product.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        size = BusinessSize.objects.create(business=self.business, name="M")
        color = BusinessColor.objects.create(
            business=self.business,
            name="Black",
        )
        self.choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=size,
            color=color,
            quantity=3,
        )
        self.duplicate = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=size,
            color=color,
            quantity=6,
        )
        private_product = Product.objects.create(
            business=self.other_business,
            name="Private workspace direct set product",
            description="Private workspace direct set product.",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        private_size = BusinessSize.objects.create(
            business=self.other_business,
            name="M",
        )
        private_color = BusinessColor.objects.create(
            business=self.other_business,
            name="Black",
        )
        self.private_choice = ProductChoice.objects.create(
            business=self.other_business,
            product=private_product,
            size=private_size,
            color=private_color,
            quantity=9,
        )
        self.url = reverse("catalog:product_list")

    def test_direct_set_is_subordinate_and_targets_each_exact_choice(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        for choice in (self.choice, self.duplicate):
            self.assertContains(
                response,
                f"ზუსტი მარაგის მითითება: არჩევანი #{choice.pk}, ზომა M, ფერი Black",
            )
            self.assertContains(
                response,
                f'id="workspace-stock-set-input-{choice.pk}"',
            )
            self.assertContains(
                response,
                f'id="workspace-stock-set-submit-{choice.pk}"',
            )
            self.assertLess(
                content.index(f'id="workspace-stock-increase-{choice.pk}"'),
                content.index(f'id="workspace-stock-set-submit-{choice.pk}"'),
            )
        self.assertContains(response, 'name="quantity"', count=2)
        self.assertContains(response, 'min="0"', count=2)
        self.assertContains(response, 'step="1"', count=2)
        self.assertNotContains(
            response,
            f'id="workspace-stock-set-input-{self.private_choice.pk}"',
        )

    def test_inactive_choice_has_no_direct_set_control(self):
        self.duplicate.is_active = False
        self.duplicate.save(update_fields=["is_active", "updated_at"])
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertContains(
            response,
            f'id="workspace-stock-set-input-{self.choice.pk}"',
        )
        self.assertNotContains(
            response,
            f'id="workspace-stock-set-input-{self.duplicate.pk}"',
        )
