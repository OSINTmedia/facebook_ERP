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
        self.assertContains(response, 'aria-label="Primary"')
        self.assertContains(response, 'aria-current="page"')
        self.assertContains(response, 'id="messages"')
        self.assertContains(response, "css/app.css")

        for label in ("Dashboard", "Products", "Add product", "Account", "Sign out"):
            self.assertContains(response, label)

        for excluded in ("ERP", "Orders", "Payments", "Public catalog"):
            self.assertNotContains(response, excluded)
