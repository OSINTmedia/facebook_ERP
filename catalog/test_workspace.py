from django.contrib.auth import get_user_model
from django.http import QueryDict
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from businesses.models import Business
from catalog.models import Product
from catalog.workspace import ProductWorkspaceState, product_workspace_products


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
