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
    ProductTag,
)
from catalog.workspace import (
    PRODUCT_DESCRIPTION_EXCERPT_LENGTH,
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
        self.assertEqual(search_form.errors["q"], ["Enter one search query."])

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
            ["Search must be 120 characters or fewer."],
        )
        self.assertFalse(too_many_tokens_form.is_valid())
        self.assertEqual(
            too_many_tokens_form.errors["q"],
            ["Search must use 8 words or fewer."],
        )

    def test_search_rejects_database_unsafe_control_characters(self):
        search_form = ProductWorkspaceSearchForm({"q": "wool\x01private"})

        self.assertFalse(search_form.is_valid())
        self.assertEqual(
            search_form.errors["q"],
            ["Search contains unsupported characters."],
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
            ["Select one lifecycle filter."],
        )
        self.assertEqual(
            search_form.errors["availability"],
            ["Select one availability filter."],
        )
        self.assertEqual(
            state.return_url,
            f'{reverse("catalog:product_list")}?q=trousers',
        )

    def test_filter_fields_expose_only_the_approved_values(self):
        self.assertEqual(
            PRODUCT_WORKSPACE_LIFECYCLE_CHOICES,
            (
                ("", "All lifecycle states"),
                (Product.Lifecycle.ACTIVE, "Active"),
                (Product.Lifecycle.DRAFT, "Draft"),
            ),
        )
        self.assertEqual(
            PRODUCT_WORKSPACE_AVAILABILITY_CHOICES,
            (
                ("", "All availability states"),
                ("available", "Available"),
                ("sold_out", "Sold out"),
            ),
        )
        search_form = ProductWorkspaceSearchForm(
            {"lifecycle": "archived", "availability": "low_stock"}
        )

        self.assertFalse(search_form.is_valid())
        self.assertIn("Select a valid choice", search_form.errors["lifecycle"][0])
        self.assertIn(
            "Select a valid choice",
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
                lifecycle_filter="archived",
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
        lifecycle=Product.Lifecycle.ACTIVE,
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
        self.assertContains(response, "<strong>1</strong> product")
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
        self.assertContains(response, "product for “black trousers”")
        self.assertContains(response, "Black trousers")
        self.assertNotContains(response, "Blue shirt")
        self.assertContains(response, "q%3Dblack%2Btrousers")
        self.assertContains(
            response,
            f'name="next" value="{expected_return_url}"',
        )
        self.assertContains(response, "Clear search", count=1)

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
        self.assertContains(response, "products for “missing”")
        self.assertContains(response, "No products match “missing”.")
        self.assertContains(response, "Try a simpler search.")
        self.assertContains(response, "Clear search", count=1)
        self.assertNotContains(response, "No products yet.")
        self.assertNotContains(
            response,
            f'href="{reverse("catalog:product_create")}?next=',
        )

    def test_search_on_an_empty_catalog_keeps_the_catalog_empty_state(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url, {"q": "missing"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["workspace_result_count"], 0)
        self.assertContains(response, "products for “missing”")
        self.assertContains(response, "No products yet.")
        self.assertNotContains(response, "No products match")
        self.assertContains(
            response,
            f'href="{reverse("catalog:product_create")}?next=',
            count=1,
        )
        self.assertContains(response, "Clear search", count=1)

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
        self.assertContains(response, "Enter one search query.")
        self.assertContains(response, "Search was not applied.")
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
        self.assertContains(response, "2 active")
        self.assertContains(response, "Lifecycle — Active")
        self.assertContains(response, "Availability — Available")
        self.assertContains(response, 'class="product-workspace-state-summary"')
        self.assertNotContains(
            response,
            'class="product-workspace-filters" open',
        )
        self.assertContains(response, "Clear search", count=1)
        self.assertContains(response, "Clear filters", count=1)
        self.assertContains(response, "Clear all", count=1)
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
            "No products match the active filters.",
        )
        self.assertContains(filter_response, "<strong>0</strong> products ·")
        self.assertContains(filter_response, "Clear filters", count=1)
        self.assertNotContains(filter_response, "Clear all")
        self.assertNotContains(filter_response, "No products yet.")
        self.assertContains(
            combined_response,
            "No products match this search and filter combination.",
        )
        self.assertContains(combined_response, "Clear all", count=1)
        self.assertNotContains(combined_response, "Clear filters")
        self.assertNotContains(combined_response, "Clear search")

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
        self.assertContains(unknown_response, "Select a valid choice")
        self.assertContains(unknown_response, "Filters were not applied.")
        self.assertContains(
            unknown_response,
            'class="product-workspace-filters" open',
        )
        self.assertNotContains(unknown_response, "Must not render unfiltered")
        self.assertFalse(repeated_response.context["workspace_query_is_valid"])
        self.assertContains(
            repeated_response,
            "Select one lifecycle filter.",
        )
        self.assertNotContains(repeated_response, "Must not render unfiltered")

    def test_true_empty_catalog_remains_distinct_with_active_filters(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            self.url,
            {"q": "missing", "availability": "sold_out"},
        )

        self.assertContains(response, "No products yet.")
        self.assertNotContains(response, "No products match")
        self.assertContains(response, "Add product", count=2)
        self.assertContains(response, "Clear all", count=1)

    def test_native_stock_fallback_updates_availability_filter_membership(self):
        product, choice = self.create_product_with_choice(
            name="Availability transition",
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
            "No products match the active filters.",
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
            "No products match the active filters.",
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
        self.assertContains(response, "1 active · 2 total stock")

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
        rendered = response.content.decode()
        self.assertLess(
            rendered.index("Lifecycle"),
            rendered.index(product.description),
        )

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
            'name="response_scope" value="workspace"',
        )
        self.assertContains(response, f'hx-post="{active_url}"', count=2)
        self.assertContains(
            response,
            'hx-target="#product-workspace-results"',
            count=2,
        )
        self.assertContains(response, 'hx-swap="outerHTML"', count=2)
        self.assertContains(
            response,
            'hx-sync="#product-workspace-results:drop"',
            count=2,
        )
        self.assertContains(response, "js/product_workspace.js")
        self.assertContains(response, "Refresh results")
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
        self.assertContains(sold_out_response, "Stock updated to 0.")
        self.assertContains(sold_out_response, "Sold out")
        self.assertContains(sold_out_response, "1 active · 0 total stock")

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
