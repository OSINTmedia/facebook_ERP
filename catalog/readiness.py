"""Buyer-question coverage from confirmed and centrally computed truth."""

from dataclasses import dataclass
from enum import StrEnum

from django.core.exceptions import ValidationError

from catalog.models import BusinessProductType, Product, ProductMaterialFact
from inventory.availability import compute_product_availability


class BuyerQuestion(StrEnum):
    PRICE = "price"
    AVAILABILITY_STOCK = "availability_stock"
    SIZE_COLOR = "size_color"
    PRODUCT_TYPE = "product_type"
    MATERIAL = "material"


class CoverageMissingReason(StrEnum):
    PRICE_MISSING = "price_missing"
    ACTIVE_CHOICES_MISSING = "active_choices_missing"
    PRODUCT_TYPE_MISSING = "product_type_missing"
    CONFIRMED_MATERIAL_MISSING = "confirmed_material_missing"


class CoverageCorrectionTarget(StrEnum):
    PRICE = "price"
    CHOICES = "choices"
    CLASSIFICATION = "classification"
    MATERIALS = "materials"


@dataclass(frozen=True)
class QuestionCoverage:
    question: BuyerQuestion
    is_answerable: bool
    missing_reason: CoverageMissingReason | None = None
    correction_target: CoverageCorrectionTarget | None = None


@dataclass(frozen=True)
class BuyerQuestionCoverage:
    items: tuple[QuestionCoverage, ...]

    def for_question(self, question: BuyerQuestion) -> QuestionCoverage:
        return next(item for item in self.items if item.question == question)


def evaluate_buyer_question_coverage(
    *,
    has_confirmed_price: bool,
    availability_stock_answerable: bool,
    size_color_answerable: bool,
    has_confirmed_product_type: bool,
    has_confirmed_material: bool,
) -> BuyerQuestionCoverage:
    """Return deterministic coverage from already-established truth signals."""

    return BuyerQuestionCoverage(
        items=(
            _coverage_item(
                question=BuyerQuestion.PRICE,
                is_answerable=has_confirmed_price,
                missing_reason=CoverageMissingReason.PRICE_MISSING,
                correction_target=CoverageCorrectionTarget.PRICE,
            ),
            _coverage_item(
                question=BuyerQuestion.AVAILABILITY_STOCK,
                is_answerable=availability_stock_answerable,
                missing_reason=CoverageMissingReason.ACTIVE_CHOICES_MISSING,
                correction_target=CoverageCorrectionTarget.CHOICES,
            ),
            _coverage_item(
                question=BuyerQuestion.SIZE_COLOR,
                is_answerable=size_color_answerable,
                missing_reason=CoverageMissingReason.ACTIVE_CHOICES_MISSING,
                correction_target=CoverageCorrectionTarget.CHOICES,
            ),
            _coverage_item(
                question=BuyerQuestion.PRODUCT_TYPE,
                is_answerable=has_confirmed_product_type,
                missing_reason=CoverageMissingReason.PRODUCT_TYPE_MISSING,
                correction_target=CoverageCorrectionTarget.CLASSIFICATION,
            ),
            _coverage_item(
                question=BuyerQuestion.MATERIAL,
                is_answerable=has_confirmed_material,
                missing_reason=CoverageMissingReason.CONFIRMED_MATERIAL_MISSING,
                correction_target=CoverageCorrectionTarget.MATERIALS,
            ),
        )
    )


def build_product_buyer_question_coverage(*, business, product):
    """Build coverage for one persisted Product in the active Business."""

    if business is None or business.pk is None:
        raise ValueError("An existing Business is required.")
    if product is None or product.pk is None:
        raise ValueError("An existing Product is required.")
    if product.business_id != business.pk:
        raise ValidationError("Product must belong to the active Business.")
    if product.lifecycle == Product.Lifecycle.ARCHIVED:
        raise ValidationError(
            "Archived Products do not have sellable buyer-question coverage."
        )

    active_choices = product.choices.filter(
        business=business,
        size__business=business,
        color__business=business,
        is_active=True,
    )
    has_active_choice = active_choices.exists()
    is_available = compute_product_availability(
        business=business,
        product=product,
    )
    has_confirmed_product_type = bool(
        product.product_type_id
        and BusinessProductType.objects.filter(
            business=business,
            pk=product.product_type_id,
        ).exists()
    )
    has_confirmed_material = ProductMaterialFact.objects.filter(
        business=business,
        product=product,
        confirmation_state=ProductMaterialFact.ConfirmationState.CONFIRMED,
    ).exists()

    return evaluate_buyer_question_coverage(
        has_confirmed_price=product.price is not None and product.price > 0,
        availability_stock_answerable=is_available or has_active_choice,
        size_color_answerable=has_active_choice,
        has_confirmed_product_type=has_confirmed_product_type,
        has_confirmed_material=has_confirmed_material,
    )


def _coverage_item(
    *,
    question,
    is_answerable,
    missing_reason,
    correction_target,
) -> QuestionCoverage:
    if is_answerable:
        missing_reason = None
        correction_target = None
    return QuestionCoverage(
        question=question,
        is_answerable=is_answerable,
        missing_reason=missing_reason,
        correction_target=correction_target,
    )
