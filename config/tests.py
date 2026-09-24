"""Smoke tests for project-level shell routes."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ShellHomeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="seller@example.com",
            password="test-password",
        )

    def test_shell_home_requires_authentication(self):
        response = self.client.get(reverse("shell_home"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('shell_home')}",
        )

    def test_authenticated_shell_home_renders_base_navigation_and_message_region(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("shell_home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "shell/home.html")
        self.assertContains(response, 'aria-label="მთავარი ნავიგაცია"')
        self.assertContains(response, 'aria-current="page"')
        self.assertContains(response, 'id="messages"')
        self.assertContains(response, "css/app.css")

        for label in (
            "მიმოხილვა",
            "პროდუქტები",
            "სიტყვარი",
            "პროდუქტის დამატება",
            "გასვლა",
        ):
            self.assertContains(response, label)

        for excluded in ("ERP", "Orders", "Payments", "Public catalog"):
            self.assertNotContains(response, excluded)

    def test_navigation_active_states_isolate_surfaces_correctly(self):
        self.client.force_login(self.user)

        # 1. Dashboard (/)
        dashboard_res = self.client.get(reverse("shell_home"))
        self.assertContains(
            dashboard_res,
            '<a class="nav-link nav-link--active" href="/" aria-current="page">მიმოხილვა</a>',
            html=True,
        )
        self.assertNotContains(
            dashboard_res,
            '<a class="nav-link nav-link--active" href="/products/" aria-current="page">პროდუქტები</a>',
            html=True,
        )

        # 2. Products (/products/)
        products_res = self.client.get(reverse("catalog:product_list"))
        self.assertContains(
            products_res,
            '<a class="nav-link nav-link--active" href="/products/" aria-current="page">პროდუქტები</a>',
            html=True,
        )
        self.assertNotContains(
            products_res,
            '<a class="nav-link nav-link--active" href="/" aria-current="page">მიმოხილვა</a>',
            html=True,
        )

        # 3. Vocabulary (/products/vocabulary/)
        vocab_res = self.client.get(reverse("catalog:choice_vocabulary"))
        self.assertContains(
            vocab_res,
            '<a class="nav-link nav-link--active" href="/products/vocabulary/" aria-current="page">სიტყვარი</a>',
            html=True,
        )
        self.assertNotContains(
            vocab_res,
            '<a class="nav-link nav-link--active" href="/" aria-current="page">მიმოხილვა</a>',
            html=True,
        )

        # 4. Product Add (/products/add/)
        create_res = self.client.get(reverse("catalog:product_create"))
        self.assertContains(
            create_res,
            '<a class="nav-link nav-link--active" href="/products/add/" aria-current="page">პროდუქტის დამატება</a>',
            html=True,
        )
        self.assertNotContains(
            create_res,
            '<a class="nav-link nav-link--active" href="/" aria-current="page">მიმოხილვა</a>',
            html=True,
        )
