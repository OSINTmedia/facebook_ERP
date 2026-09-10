from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase

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
from catalog.readiness import (
    BuyerQuestion,
    CoverageCorrectionTarget,
    CoverageMissingReason,
    build_product_buyer_question_coverage,
    evaluate_buyer_question_coverage,
)
from catalog.recognition import RecognitionCandidate, SemanticDestination
from inventory.availability import compute_product_availability


class BuyerQuestionCoverageTruthMatrixTests(SimpleTestCase):
    def test_missing_truth_returns_structured_gaps_without_a_score(self):
        coverage = evaluate_buyer_question_coverage(
            has_confirmed_price=False,
            availability_stock_answerable=False,
            size_color_answerable=False,
            has_confirmed_product_type=False,
            has_confirmed_material=False,
        )

        expected_gaps = {
            BuyerQuestion.PRICE: (
                CoverageMissingReason.PRICE_MISSING,
                CoverageCorrectionTarget.PRICE,
            ),
            BuyerQuestion.AVAILABILITY_STOCK: (
                CoverageMissingReason.ACTIVE_CHOICES_MISSING,
                CoverageCorrectionTarget.CHOICES,
            ),
            BuyerQuestion.SIZE_COLOR: (
                CoverageMissingReason.ACTIVE_CHOICES_MISSING,
                CoverageCorrectionTarget.CHOICES,
            ),
            BuyerQuestion.PRODUCT_TYPE: (
                CoverageMissingReason.PRODUCT_TYPE_MISSING,
                CoverageCorrectionTarget.CLASSIFICATION,
            ),
            BuyerQuestion.MATERIAL: (
                CoverageMissingReason.CONFIRMED_MATERIAL_MISSING,
                CoverageCorrectionTarget.MATERIALS,
            ),
        }
        self.assertEqual(len(coverage.items), len(expected_gaps))
        self.assertFalse(hasattr(coverage, "score"))
        self.assertFalse(hasattr(coverage, "percentage"))
        for question, (reason, target) in expected_gaps.items():
            with self.subTest(question=question):
                item = coverage.for_question(question)
                self.assertFalse(item.is_answerable)
                self.assertEqual(item.missing_reason, reason)
                self.assertEqual(item.correction_target, target)

    def test_confirmed_truth_is_deterministic_and_clears_gap_metadata(self):
        inputs = {
            "has_confirmed_price": True,
            "availability_stock_answerable": True,
            "size_color_answerable": True,
            "has_confirmed_product_type": True,
            "has_confirmed_material": True,
        }

        first = evaluate_buyer_question_coverage(**inputs)
        second = evaluate_buyer_question_coverage(**inputs)

        self.assertEqual(first, second)
        for item in first.items:
            self.assertTrue(item.is_answerable)
            self.assertIsNone(item.missing_reason)
            self.assertIsNone(item.correction_target)


class ProductBuyerQuestionCoverageTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="readiness-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="readiness-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Readiness Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Readiness Studio",
        )
        self.size = BusinessSize.objects.create(business=self.business, name="M")
        self.color = BusinessColor.objects.create(
            business=self.business,
            name="Black",
        )

    def create_product(self, **overrides):
        values = {
            "business": self.business,
            "name": "Readiness product",
            "description": "Cotton dress",
            "lifecycle": Product.Lifecycle.ACTIVE,
        }
        values.update(overrides)
        return Product.objects.create(**values)

    def create_choice(self, *, product, quantity=1, is_active=True):
        return ProductChoice.objects.create(
            business=self.business,
            product=product,
            size=self.size,
            color=self.color,
            quantity=quantity,
            is_active=is_active,
        )

    def test_confirmed_product_truth_answers_every_supported_question(self):
        product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Dress",
        )
        product = self.create_product(
            product_type=product_type,
            price=Decimal("125.00"),
        )
        self.create_choice(product=product, quantity=3)
        ProductMaterialFact.objects.create(
            business=self.business,
            product=product,
            canonical_material="Cotton",
            original_text="cotton",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )

        coverage = build_product_buyer_question_coverage(
            business=self.business,
            product=product,
        )

        self.assertTrue(all(item.is_answerable for item in coverage.items))

    def test_sold_out_and_duplicate_partial_stock_keep_exact_choice_truth(self):
        product = self.create_product()
        sold_out_choice = self.create_choice(product=product, quantity=0)

        with patch(
            "catalog.readiness.compute_product_availability",
            wraps=compute_product_availability,
        ) as availability_service:
            sold_out_coverage = build_product_buyer_question_coverage(
                business=self.business,
                product=product,
            )

        availability_service.assert_called_once_with(
            business=self.business,
            product=product,
        )
        self.assertTrue(
            sold_out_coverage.for_question(
                BuyerQuestion.AVAILABILITY_STOCK
            ).is_answerable
        )
        self.assertTrue(
            sold_out_coverage.for_question(BuyerQuestion.SIZE_COLOR).is_answerable
        )

        stocked_duplicate = self.create_choice(product=product, quantity=4)
        partial_coverage = build_product_buyer_question_coverage(
            business=self.business,
            product=product,
        )

        self.assertTrue(
            partial_coverage.for_question(
                BuyerQuestion.AVAILABILITY_STOCK
            ).is_answerable
        )
        self.assertEqual(
            list(product.choices.order_by("id").values_list("id", flat=True)),
            [sold_out_choice.id, stocked_duplicate.id],
        )

    def test_missing_or_inactive_choices_leave_stock_and_size_color_gaps(self):
        product = self.create_product()
        self.create_choice(product=product, quantity=5, is_active=False)

        coverage = build_product_buyer_question_coverage(
            business=self.business,
            product=product,
        )

        for question in (
            BuyerQuestion.AVAILABILITY_STOCK,
            BuyerQuestion.SIZE_COLOR,
        ):
            with self.subTest(question=question):
                item = coverage.for_question(question)
                self.assertFalse(item.is_answerable)
                self.assertEqual(
                    item.missing_reason,
                    CoverageMissingReason.ACTIVE_CHOICES_MISSING,
                )

    def test_tag_and_unconfirmed_candidate_do_not_improve_coverage(self):
        product = self.create_product()
        tag = BusinessTag.objects.create(business=self.business, name="Summer")
        ProductTag.objects.create(
            business=self.business,
            product=product,
            tag=tag,
        )
        candidate = RecognitionCandidate(
            destination=SemanticDestination.MATERIAL,
            canonical_value="Cotton",
            observed_text="cotton",
            span_start=0,
            span_end=6,
        )

        coverage = build_product_buyer_question_coverage(
            business=self.business,
            product=product,
        )

        self.assertFalse(candidate.is_confirmed)
        self.assertFalse(
            coverage.for_question(BuyerQuestion.PRODUCT_TYPE).is_answerable
        )
        self.assertFalse(coverage.for_question(BuyerQuestion.MATERIAL).is_answerable)

    def test_cross_business_product_is_rejected(self):
        product = self.create_product(business=self.other_business)

        with self.assertRaisesMessage(
            ValidationError,
            "Product must belong to the active Business.",
        ):
            build_product_buyer_question_coverage(
                business=self.business,
                product=product,
            )

    def test_cross_business_related_truth_is_not_consumed(self):
        other_type = BusinessProductType.objects.create(
            business=self.other_business,
            name="Other dress",
        )
        other_size = BusinessSize.objects.create(
            business=self.other_business,
            name="XL",
        )
        product = self.create_product()
        choice = self.create_choice(product=product, quantity=7)
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

        coverage = build_product_buyer_question_coverage(
            business=self.business,
            product=product,
        )

        self.assertFalse(
            coverage.for_question(BuyerQuestion.PRODUCT_TYPE).is_answerable
        )
        self.assertFalse(coverage.for_question(BuyerQuestion.MATERIAL).is_answerable)
        self.assertFalse(
            coverage.for_question(BuyerQuestion.AVAILABILITY_STOCK).is_answerable
        )
        self.assertFalse(
            coverage.for_question(BuyerQuestion.SIZE_COLOR).is_answerable
        )

    def test_coverage_evaluation_does_not_write(self):
        product = self.create_product(price=Decimal("50.00"))
        choice = self.create_choice(product=product, quantity=2)
        product_snapshot = (product.updated_at, product.price, product.lifecycle)
        choice_snapshot = (choice.updated_at, choice.quantity, choice.is_active)
        object_counts = (
            Product.objects.count(),
            ProductChoice.objects.count(),
            ProductMaterialFact.objects.count(),
        )

        build_product_buyer_question_coverage(
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
