from django.contrib.auth import get_user_model
from django.test import TestCase


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
