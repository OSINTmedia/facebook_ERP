from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from businesses.models import Business


class BusinessModelTests(TestCase):
    def test_business_belongs_to_custom_user_model(self):
        user_model = get_user_model()
        owner = user_model.objects.create_user(
            email="seller@example.com",
            password="test-password",
        )

        business = Business.objects.create(owner=owner, name="Seller Studio")

        self.assertEqual(business.owner, owner)
        self.assertEqual(owner.businesses.get(), business)
        self.assertEqual(
            Business._meta.get_field("owner").remote_field.model,
            user_model,
        )

    def test_business_requires_owner(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Business.objects.create(name="Ownerless Studio")

    def test_business_requires_name(self):
        user_model = get_user_model()
        owner = user_model.objects.create_user(
            email="seller@example.com",
            password="test-password",
        )
        business = Business(owner=owner, name="")

        with self.assertRaises(ValidationError):
            business.full_clean()

    def test_business_string_uses_name(self):
        user_model = get_user_model()
        owner = user_model.objects.create_user(
            email="seller@example.com",
            password="test-password",
        )
        business = Business.objects.create(owner=owner, name="Seller Studio")

        self.assertEqual(str(business), "Seller Studio")
