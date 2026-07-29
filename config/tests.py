"""Smoke tests for project-level shell routes."""
from django.test import SimpleTestCase
from django.urls import reverse


class ShellHomeTests(SimpleTestCase):
    def test_shell_home_renders_base_navigation_and_message_region(self):
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
