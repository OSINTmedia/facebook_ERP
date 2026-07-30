from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserModelTests(TestCase):
    def test_user_is_identified_by_email(self):
        user_model = get_user_model()
        field_names = {field.name for field in user_model._meta.fields}

        self.assertEqual(user_model.USERNAME_FIELD, "email")
        self.assertEqual(user_model.REQUIRED_FIELDS, [])
        self.assertNotIn("username", field_names)

    def test_create_user_normalizes_email_and_sets_password(self):
        user_model = get_user_model()

        user = user_model.objects.create_user(
            email="Seller@EXAMPLE.COM",
            password="test-password",
        )

        self.assertEqual(user.email, "seller@example.com")
        self.assertTrue(user.check_password("test-password"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(str(user), "seller@example.com")

    def test_create_user_requires_email(self):
        user_model = get_user_model()

        with self.assertRaisesMessage(ValueError, "The email address must be set."):
            user_model.objects.create_user(email="", password="test-password")

    def test_create_superuser_sets_required_flags(self):
        user_model = get_user_model()

        user = user_model.objects.create_superuser(
            email="owner@example.com",
            password="test-password",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_rejects_invalid_staff_flags(self):
        user_model = get_user_model()

        with self.assertRaisesMessage(ValueError, "Superuser must have is_staff=True."):
            user_model.objects.create_superuser(
                email="owner@example.com",
                password="test-password",
                is_staff=False,
            )

        with self.assertRaisesMessage(
            ValueError,
            "Superuser must have is_superuser=True.",
        ):
            user_model.objects.create_superuser(
                email="owner@example.com",
                password="test-password",
                is_superuser=False,
            )


class SellerAuthenticationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="seller@example.com",
            password="test-password",
        )

    def test_login_page_renders_email_password_form_without_seller_nav(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertContains(response, 'type="email"')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'type="password"')

        for label in ("Dashboard", "Products", "Add product", "Account", "Sign out"):
            self.assertNotContains(response, label)

    def test_valid_login_accepts_email_and_redirects_to_shell(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "SELLER@example.com",
                "password": "test-password",
            },
        )

        self.assertRedirects(response, reverse("shell_home"))

    def test_invalid_login_shows_validation_error(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": self.user.email,
                "password": "wrong-password",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertTrue(response.context["form"].non_field_errors())

    def test_login_uses_safe_internal_next_url(self):
        response = self.client.post(
            f"{reverse('accounts:login')}?next={reverse('shell_home')}",
            {
                "username": self.user.email,
                "password": "test-password",
            },
        )

        self.assertRedirects(response, reverse("shell_home"))

    def test_login_rejects_external_next_url(self):
        response = self.client.post(
            f"{reverse('accounts:login')}?next=https://example.com/escape",
            {
                "username": self.user.email,
                "password": "test-password",
            },
        )

        self.assertRedirects(response, reverse("shell_home"))
        self.assertNotIn("example.com", response["Location"])

    def test_authenticated_user_is_redirected_away_from_login_page(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:login"))

        self.assertRedirects(response, reverse("shell_home"))

    def test_logout_requires_post(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 405)

    def test_post_logout_ends_session_and_redirects_to_login(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("accounts:login"))
        shell_response = self.client.get(reverse("shell_home"))
        self.assertRedirects(
            shell_response,
            f"{reverse('accounts:login')}?next={reverse('shell_home')}",
        )
