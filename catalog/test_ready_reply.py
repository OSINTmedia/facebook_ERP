from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from businesses.models import Business
from catalog.models import (
    BusinessColor,
    BusinessProductType,
    BusinessSize,
    BusinessTag,
    Product,
    ProductChoice,
    ProductMaterialFact,
    ProductTag,
)
from catalog.readiness import CoverageCorrectionTarget
from catalog.ready_reply import (
    ReadyReplyComponentKind,
    ReadyReplyNoteCode,
    build_product_ready_reply,
)
from catalog.recognition import RecognitionCandidate, SemanticDestination
from inventory.availability import compute_product_availability


class ProductReadyReplyTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="reply-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="reply-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Reply Studio",
            default_currency="GEL",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Reply Studio",
        )
        self.size_m = BusinessSize.objects.create(
            business=self.business,
            name="M",
        )
        self.size_l = BusinessSize.objects.create(
            business=self.business,
            name="L",
        )
        self.black = BusinessColor.objects.create(
            business=self.business,
            name="Black",
        )

    def create_product(self, **overrides):
        values = {
            "business": self.business,
            "name": "Reply product",
            "description": "Cotton dress",
            "lifecycle": Product.Lifecycle.ACTIVE,
        }
        values.update(overrides)
        return Product.objects.create(**values)

    def create_choice(
        self,
        *,
        product,
        size=None,
        color=None,
        quantity=1,
        is_active=True,
        business=None,
    ):
        return ProductChoice.objects.create(
            business=business or self.business,
            product=product,
            size=size or self.size_m,
            color=color or self.black,
            quantity=quantity,
            is_active=is_active,
        )

    def test_confirmed_truth_produces_deterministic_ordered_reply(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Dress",
        )
        product = self.create_product(
            product_type=product_type,
            price=Decimal("125.00"),
        )
        choice = self.create_choice(product=product, quantity=3)
        ProductMaterialFact.objects.create(
            business=self.business,
            product=product,
            canonical_material="Cotton",
            percentage=80,
            original_text="80% cotton",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )

        first = build_product_ready_reply(
            business=self.business,
            product=product,
        )
        second = build_product_ready_reply(
            business=self.business,
            product=product,
        )

        self.assertEqual(first, second)
        self.assertEqual(
            tuple(component.kind for component in first.components),
            (
                ReadyReplyComponentKind.DESCRIPTION,
                ReadyReplyComponentKind.PRODUCT_TYPE,
                ReadyReplyComponentKind.PRICE,
                ReadyReplyComponentKind.MATERIAL,
                ReadyReplyComponentKind.CHOICES,
                ReadyReplyComponentKind.AVAILABILITY,
            ),
        )
        self.assertEqual(first.choices[0].choice_id, choice.pk)
        self.assertEqual(first.seller_notes, ())
        self.assertEqual(
            first.buyer_text,
            "აღწერა: Cotton dress\n"
            "პროდუქტის ტიპი: Dress.\n"
            "ფასი: 125.00 GEL.\n"
            "მასალა: Cotton (80%).\n"
            "ზომა, ფერი და მარაგი: M / Black — 3 ც.\n"
            "ხელმისაწვდომობა: მარაგშია.",
        )

    def test_partial_and_sold_out_wording_uses_central_availability(self):
        product = self.create_product()
        self.create_choice(product=product, size=self.size_l, quantity=2)
        self.create_choice(product=product, size=self.size_m, quantity=0)

        with patch(
            "catalog.ready_reply.compute_product_availability",
            wraps=compute_product_availability,
        ) as availability_service:
            partial_reply = build_product_ready_reply(
                business=self.business,
                product=product,
            )

        availability_service.assert_called_once_with(
            business=self.business,
            product=product,
        )
        self.assertIn(
            "ხელმისაწვდომობა: მარაგშია, თუმცა ზოგი არჩევანი ამოწურულია.",
            partial_reply.buyer_text,
        )

        ProductChoice.objects.filter(product=product).update(quantity=0)
        sold_out_reply = build_product_ready_reply(
            business=self.business,
            product=product,
        )

        self.assertIn(
            "ხელმისაწვდომობა: ამოწურულია.",
            sold_out_reply.buyer_text,
        )
        self.assertNotIn("ხელმისაწვდომობა: მარაგშია.", sold_out_reply.buyer_text)

    def test_missing_truth_is_omitted_and_reported_only_to_seller(self):
        product = self.create_product(price=None)

        reply = build_product_ready_reply(
            business=self.business,
            product=product,
        )

        self.assertEqual(
            tuple(note.code for note in reply.seller_notes),
            (
                ReadyReplyNoteCode.PRICE_MISSING,
                ReadyReplyNoteCode.ACTIVE_CHOICES_MISSING,
                ReadyReplyNoteCode.PRODUCT_TYPE_MISSING,
                ReadyReplyNoteCode.CONFIRMED_MATERIAL_MISSING,
            ),
        )
        self.assertNotIn("ფასი:", reply.buyer_text)
        self.assertNotIn("0.00", reply.buyer_text)
        self.assertNotIn("free", reply.buyer_text.lower())
        for note in reply.seller_notes:
            self.assertNotIn(note.text, reply.buyer_text)

    def test_tag_and_unconfirmed_candidate_never_enter_buyer_text(self):
        product = self.create_product()
        tag = BusinessTag.objects.create(business=self.business, name="Summer")
        ProductTag.objects.create(
            business=self.business,
            product=product,
            tag=tag,
        )
        candidate = RecognitionCandidate(
            destination=SemanticDestination.MATERIAL,
            canonical_value="Linen",
            observed_text="linen",
            span_start=0,
            span_end=5,
        )

        reply = build_product_ready_reply(
            business=self.business,
            product=product,
        )

        self.assertFalse(candidate.is_confirmed)
        self.assertNotIn("Summer", reply.buyer_text)
        self.assertNotIn("Linen", reply.buyer_text)

    def test_duplicate_choices_preserve_ids_without_quantity_aggregation(self):
        product = self.create_product()
        first_choice = self.create_choice(product=product, quantity=1)
        second_choice = self.create_choice(product=product, quantity=4)

        reply = build_product_ready_reply(
            business=self.business,
            product=product,
        )

        self.assertEqual(
            tuple(choice.choice_id for choice in reply.choices),
            (first_choice.pk, second_choice.pk),
        )
        choice_component = next(
            component
            for component in reply.components
            if component.kind == ReadyReplyComponentKind.CHOICES
        )
        self.assertEqual(
            choice_component.choice_ids,
            (first_choice.pk, second_choice.pk),
        )
        self.assertIn("M / Black — რაოდენობა დასაზუსტებელია", reply.buyer_text)
        self.assertNotIn("M / Black — 5", reply.buyer_text)
        duplicate_note = next(
            note
            for note in reply.seller_notes
            if note.code == ReadyReplyNoteCode.DUPLICATE_CHOICE_AMBIGUITY
        )
        self.assertEqual(
            duplicate_note.choice_ids,
            (first_choice.pk, second_choice.pk),
        )
        self.assertEqual(
            duplicate_note.correction_target,
            CoverageCorrectionTarget.CHOICES,
        )
        self.assertNotIn(duplicate_note.text, reply.buyer_text)

    def test_inactive_choices_are_excluded_from_reply_truth(self):
        product = self.create_product()
        inactive = self.create_choice(product=product, quantity=9, is_active=False)

        reply = build_product_ready_reply(
            business=self.business,
            product=product,
        )

        self.assertEqual(reply.choices, ())
        self.assertNotIn("9 ც.", reply.buyer_text)
        active_choice_note = next(
            note
            for note in reply.seller_notes
            if note.code == ReadyReplyNoteCode.ACTIVE_CHOICES_MISSING
        )
        self.assertEqual(active_choice_note.choice_ids, ())
        self.assertNotIn(str(inactive.pk), reply.buyer_text)

    def test_draft_product_never_claims_availability(self):
        product = self.create_product(lifecycle=Product.Lifecycle.DRAFT)
        self.create_choice(product=product, quantity=8)

        reply = build_product_ready_reply(
            business=self.business,
            product=product,
        )

        self.assertIn(
            "ხელმისაწვდომობა: ამჟამად გასაყიდად აქტიური არ არის.",
            reply.buyer_text,
        )
        self.assertNotIn("ხელმისაწვდომობა: მარაგშია.", reply.buyer_text)

    def test_description_stays_plain_text_and_does_not_promote_material(self):
        product = self.create_product(
            description="  <strong>Cotton</strong>   dress  ",
        )

        reply = build_product_ready_reply(
            business=self.business,
            product=product,
        )

        self.assertIn("აღწერა: <strong>Cotton</strong> dress", reply.buyer_text)
        self.assertNotIn("მასალა:", reply.buyer_text)
        self.assertTrue(
            any(
                note.code == ReadyReplyNoteCode.CONFIRMED_MATERIAL_MISSING
                for note in reply.seller_notes
            )
        )

    def test_cross_business_product_is_rejected_without_reply_content(self):
        product = self.create_product(business=self.other_business)

        with self.assertRaisesMessage(
            ValidationError,
            "Product must belong to the active Business.",
        ):
            build_product_ready_reply(
                business=self.business,
                product=product,
            )

    def test_cross_business_related_truth_is_excluded(self):
        other_type = BusinessProductType.objects.create(
            business=self.other_business,
            name="Other coat",
        )
        product = self.create_product()
        choice = self.create_choice(product=product, quantity=7)
        other_size = BusinessSize.objects.create(
            business=self.other_business,
            name="XL",
        )
        material = ProductMaterialFact.objects.create(
            business=self.business,
            product=product,
            canonical_material="Cotton",
            original_text="cotton",
            source=ProductMaterialFact.Source.MANUAL,
        )
        Product.objects.filter(pk=product.pk).update(product_type=other_type)
        ProductChoice.objects.filter(pk=choice.pk).update(size=other_size)
        ProductMaterialFact.objects.filter(pk=material.pk).update(
            business=self.other_business
        )
        product.refresh_from_db()

        reply = build_product_ready_reply(
            business=self.business,
            product=product,
        )

        self.assertNotIn("Other coat", reply.buyer_text)
        self.assertNotIn(
            ReadyReplyComponentKind.MATERIAL,
            tuple(component.kind for component in reply.components),
        )
        self.assertNotIn("7 ც.", reply.buyer_text)
        self.assertEqual(reply.choices, ())

    def test_reply_build_does_not_write(self):
        product = self.create_product(price=Decimal("50.00"))
        choice = self.create_choice(product=product, quantity=2)
        product_snapshot = (product.updated_at, product.price, product.lifecycle)
        choice_snapshot = (choice.updated_at, choice.quantity, choice.is_active)
        object_counts = (
            Product.objects.count(),
            ProductChoice.objects.count(),
            ProductMaterialFact.objects.count(),
        )

        build_product_ready_reply(
            business=self.business,
            product=product,
        )

        product.refresh_from_db()
        choice.refresh_from_db()
        self.assertEqual(
            (product.updated_at, product.price, product.lifecycle),
            product_snapshot,
        )
        self.assertEqual(
            (choice.updated_at, choice.quantity, choice.is_active),
            choice_snapshot,
        )
        self.assertEqual(
            (
                Product.objects.count(),
                ProductChoice.objects.count(),
                ProductMaterialFact.objects.count(),
            ),
            object_counts,
        )
