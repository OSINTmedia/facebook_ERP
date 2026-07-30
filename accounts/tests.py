from io import StringIO

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse


DEMO_TEST_EMAIL = "demo-seller@example.test"
DEMO_TEST_PASSWORD = "synthetic-test-password"
DEMO_TEST_NEW_PASSWORD = "synthetic-test-password-updated"


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


class DemoAccessSettingsTests(SimpleTestCase):
    @override_settings(
        DEMO_ACCESS_ENABLED=False,
        DEMO_USER_EMAIL="",
        DEMO_USER_PASSWORD="",
    )
    def test_demo_access_settings_default_to_disabled_state(self):
        self.assertFalse(settings.DEMO_ACCESS_ENABLED)
        self.assertEqual(settings.DEMO_USER_EMAIL, "")
        self.assertEqual(settings.DEMO_USER_PASSWORD, "")


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

    @override_settings(
        DEMO_ACCESS_ENABLED=False,
        DEMO_USER_EMAIL=DEMO_TEST_EMAIL,
        DEMO_USER_PASSWORD=DEMO_TEST_PASSWORD,
    )
    def test_login_page_hides_demo_credentials_when_demo_access_is_disabled(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Demo access")
        self.assertNotContains(response, DEMO_TEST_EMAIL)
        self.assertNotContains(response, DEMO_TEST_PASSWORD)

    @override_settings(
        DEMO_ACCESS_ENABLED=True,
        DEMO_USER_EMAIL=DEMO_TEST_EMAIL,
        DEMO_USER_PASSWORD=DEMO_TEST_PASSWORD,
    )
    def test_login_page_shows_configured_demo_credentials_when_enabled(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Demo access")
        self.assertContains(response, "Synthetic demo credentials")
        self.assertContains(response, DEMO_TEST_EMAIL)
        self.assertContains(response, DEMO_TEST_PASSWORD)

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


class SeedDemoUserCommandTests(TestCase):
    @override_settings(
        DEMO_ACCESS_ENABLED=False,
        DEMO_USER_EMAIL=DEMO_TEST_EMAIL,
        DEMO_USER_PASSWORD=DEMO_TEST_PASSWORD,
    )
    def test_command_refuses_disabled_demo_access(self):
        with self.assertRaisesMessage(CommandError, "Demo access is disabled."):
            call_command("seed_demo_user")

    @override_settings(
        DEMO_ACCESS_ENABLED=True,
        DEMO_USER_EMAIL="",
        DEMO_USER_PASSWORD=DEMO_TEST_PASSWORD,
    )
    def test_command_refuses_missing_email_configuration(self):
        with self.assertRaisesMessage(
            CommandError,
            "DEMO_USER_EMAIL and DEMO_USER_PASSWORD must be configured.",
        ):
            call_command("seed_demo_user")

    @override_settings(
        DEMO_ACCESS_ENABLED=True,
        DEMO_USER_EMAIL=DEMO_TEST_EMAIL,
        DEMO_USER_PASSWORD="",
    )
    def test_command_refuses_missing_password_configuration(self):
        with self.assertRaisesMessage(
            CommandError,
            "DEMO_USER_EMAIL and DEMO_USER_PASSWORD must be configured.",
        ):
            call_command("seed_demo_user")

    @override_settings(
        DEMO_ACCESS_ENABLED=True,
        DEMO_USER_EMAIL=DEMO_TEST_EMAIL.upper(),
        DEMO_USER_PASSWORD=DEMO_TEST_PASSWORD,
    )
    def test_first_run_creates_one_regular_active_user(self):
        output = StringIO()

        call_command("seed_demo_user", stdout=output)

        user_model = get_user_model()
        self.assertEqual(user_model.objects.count(), 1)
        user = user_model.objects.get(email=DEMO_TEST_EMAIL)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(DEMO_TEST_PASSWORD))
        self.assertNotEqual(user.password, DEMO_TEST_PASSWORD)
        self.assertNotIn(DEMO_TEST_PASSWORD, user.password)
        self.assertIn("Demo user created.", output.getvalue())
        self.assertNotIn(DEMO_TEST_PASSWORD, output.getvalue())

    @override_settings(
        DEMO_ACCESS_ENABLED=True,
        DEMO_USER_EMAIL=DEMO_TEST_EMAIL,
        DEMO_USER_PASSWORD=DEMO_TEST_PASSWORD,
    )
    def test_repeated_run_does_not_duplicate_user(self):
        call_command("seed_demo_user", stdout=StringIO())
        call_command("seed_demo_user", stdout=StringIO())

        self.assertEqual(
            get_user_model().objects.filter(email=DEMO_TEST_EMAIL).count(),
            1,
        )

    @override_settings(
        DEMO_ACCESS_ENABLED=True,
        DEMO_USER_EMAIL=DEMO_TEST_EMAIL,
        DEMO_USER_PASSWORD=DEMO_TEST_NEW_PASSWORD,
    )
    def test_repeated_run_updates_password_and_removes_admin_privileges(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            email=DEMO_TEST_EMAIL,
            password=DEMO_TEST_PASSWORD,
            is_active=False,
            is_staff=True,
            is_superuser=True,
        )
        previous_password_hash = user.password

        output = StringIO()
        call_command("seed_demo_user", stdout=output)

        user.refresh_from_db()
        self.assertEqual(user_model.objects.filter(email=DEMO_TEST_EMAIL).count(), 1)
        self.assertNotEqual(user.password, previous_password_hash)
        self.assertNotEqual(user.password, DEMO_TEST_NEW_PASSWORD)
        self.assertNotIn(DEMO_TEST_NEW_PASSWORD, user.password)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(DEMO_TEST_NEW_PASSWORD))
        self.assertFalse(user.check_password(DEMO_TEST_PASSWORD))
        self.assertIsNotNone(
            authenticate(email=DEMO_TEST_EMAIL, password=DEMO_TEST_NEW_PASSWORD)
        )
        self.assertIn("Demo user updated.", output.getvalue())
        self.assertNotIn(DEMO_TEST_NEW_PASSWORD, output.getvalue())
