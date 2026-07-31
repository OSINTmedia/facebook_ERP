from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import Http404
from django.test import TestCase

from businesses.models import Business
from businesses.selectors import (
    MultipleBusinessesUnsupported,
    businesses_owned_by,
    get_owned_business_or_404,
    resolve_active_business,
)


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


class BusinessSelectorTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="other-owner@example.com",
            password="test-password",
        )

    def test_businesses_owned_by_returns_only_authenticated_users_businesses(self):
        first_business = Business.objects.create(owner=self.owner, name="First Studio")
        second_business = Business.objects.create(
            owner=self.owner,
            name="Second Studio",
        )
        Business.objects.create(owner=self.other_owner, name="Other Studio")

        businesses = list(businesses_owned_by(self.owner))

        self.assertEqual(businesses, [first_business, second_business])

    def test_businesses_owned_by_returns_empty_queryset_for_anonymous_user(self):
        Business.objects.create(owner=self.owner, name="Seller Studio")

        businesses = businesses_owned_by(AnonymousUser())

        self.assertEqual(list(businesses), [])

    def test_resolve_active_business_returns_none_without_creating_business(self):
        self.assertEqual(Business.objects.count(), 0)

        business = resolve_active_business(self.owner)

        self.assertIsNone(business)
        self.assertEqual(Business.objects.count(), 0)

    def test_resolve_active_business_ignores_other_owners_businesses(self):
        other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )

        business = resolve_active_business(self.owner)

        self.assertIsNone(business)
        self.assertEqual(list(businesses_owned_by(self.owner)), [])
        self.assertEqual(Business.objects.get(), other_business)

    def test_resolve_active_business_returns_single_owned_business(self):
        owned_business = Business.objects.create(owner=self.owner, name="Seller Studio")
        Business.objects.create(owner=self.other_owner, name="Other Studio")

        business = resolve_active_business(self.owner)

        self.assertEqual(business, owned_business)

    def test_resolve_active_business_requires_approved_policy_for_multiple_businesses(
        self,
    ):
        Business.objects.create(owner=self.owner, name="First Studio")
        Business.objects.create(owner=self.owner, name="Second Studio")

        with self.assertRaisesMessage(
            MultipleBusinessesUnsupported,
            "Multiple businesses require an approved active-business policy.",
        ):
            resolve_active_business(self.owner)

    def test_get_owned_business_or_404_returns_owned_business_by_id(self):
        owned_business = Business.objects.create(owner=self.owner, name="Seller Studio")

        business = get_owned_business_or_404(self.owner, owned_business.id)

        self.assertEqual(business, owned_business)

    def test_get_owned_business_or_404_hides_another_owners_business(self):
        other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Studio",
        )

        with self.assertRaises(Http404):
            get_owned_business_or_404(self.owner, other_business.id)

    def test_get_owned_business_or_404_hides_missing_business_id(self):
        with self.assertRaises(Http404):
            get_owned_business_or_404(self.owner, 999)

    def test_get_owned_business_or_404_hides_business_from_anonymous_user(self):
        owned_business = Business.objects.create(owner=self.owner, name="Seller Studio")

        with self.assertRaises(Http404):
            get_owned_business_or_404(AnonymousUser(), owned_business.id)
