"""Deterministic Ready Reply content from confirmed Product truth."""

from dataclasses import dataclass
from enum import StrEnum

from django.core.exceptions import ValidationError

from catalog.models import BusinessProductType, Product, ProductMaterialFact
from catalog.readiness import (
    BuyerQuestion,
    CoverageCorrectionTarget,
    CoverageMissingReason,
    evaluate_buyer_question_coverage,
)
from inventory.availability import compute_product_availability


class ReadyReplyComponentKind(StrEnum):
    DESCRIPTION = "description"
    PRODUCT_TYPE = "product_type"
    PRICE = "price"
    MATERIAL = "material"
    CHOICES = "choices"
    AVAILABILITY = "availability"


class ReadyReplyNoteCode(StrEnum):
    PRICE_MISSING = CoverageMissingReason.PRICE_MISSING
    ACTIVE_CHOICES_MISSING = CoverageMissingReason.ACTIVE_CHOICES_MISSING
    PRODUCT_TYPE_MISSING = CoverageMissingReason.PRODUCT_TYPE_MISSING
    CONFIRMED_MATERIAL_MISSING = (
        CoverageMissingReason.CONFIRMED_MATERIAL_MISSING
    )
    DUPLICATE_CHOICE_AMBIGUITY = "duplicate_choice_ambiguity"


@dataclass(frozen=True)
class ReadyReplyChoice:
    choice_id: int
    size_name: str
    color_name: str
    quantity: int


@dataclass(frozen=True)
class ReadyReplyComponent:
    kind: ReadyReplyComponentKind
    text: str
    choice_ids: tuple[int, ...] = ()


@dataclass(frozen=True)
class ReadyReplySellerNote:
    code: ReadyReplyNoteCode
    text: str
    correction_target: CoverageCorrectionTarget | None = None
    choice_ids: tuple[int, ...] = ()


@dataclass(frozen=True)
class ReadyReply:
    components: tuple[ReadyReplyComponent, ...]
    seller_notes: tuple[ReadyReplySellerNote, ...]
    choices: tuple[ReadyReplyChoice, ...]

    @property
    def buyer_text(self) -> str:
        return "\n".join(component.text for component in self.components)


_MISSING_NOTE_TEXT = {
    CoverageMissingReason.PRICE_MISSING: (
        "ფასი აკლია — პასუხში ფასი არ დამატებულა."
    ),
    CoverageMissingReason.ACTIVE_CHOICES_MISSING: (
        "აქტიური ზომა/ფერი აკლია — მარაგისა და არჩევანის პასუხი არ დამატებულა."
    ),
    CoverageMissingReason.PRODUCT_TYPE_MISSING: (
        "პროდუქტის ტიპი აკლია — პასუხში ტიპი არ დამატებულა."
    ),
    CoverageMissingReason.CONFIRMED_MATERIAL_MISSING: (
        "დადასტურებული მასალა აკლია — პასუხში მასალა არ დამატებულა."
    ),
}


def build_product_ready_reply(*, business, product) -> ReadyReply:
    """Build one read-only reply for a persisted Product in the active Business."""

    if business is None or business.pk is None:
        raise ValueError("An existing Business is required.")
    if product is None or product.pk is None:
        raise ValueError("An existing Product is required.")
    if product.business_id != business.pk:
        raise ValidationError("Product must belong to the active Business.")

    choices = tuple(
        ReadyReplyChoice(
            choice_id=choice.pk,
            size_name=choice.size.name,
            color_name=choice.color.name,
            quantity=choice.quantity,
        )
        for choice in product.choices.filter(
            business=business,
            size__business=business,
            color__business=business,
            is_active=True,
        ).select_related("size", "color")
    )
    choices = tuple(
        sorted(
            choices,
            key=lambda choice: (
                _normalized_label(choice.size_name),
                _normalized_label(choice.color_name),
                choice.choice_id,
            ),
        )
    )

    product_type_name = None
    if product.product_type_id:
        product_type_name = BusinessProductType.objects.filter(
            business=business,
            pk=product.product_type_id,
        ).values_list("name", flat=True).first()

    materials = tuple(
        ProductMaterialFact.objects.filter(
            business=business,
            product=product,
            confirmation_state=ProductMaterialFact.ConfirmationState.CONFIRMED,
        ).order_by("canonical_material", "percentage", "id")
    )
    is_available = compute_product_availability(
        business=business,
        product=product,
    )
    coverage = evaluate_buyer_question_coverage(
        has_confirmed_price=product.price is not None and product.price > 0,
        availability_stock_answerable=is_available or bool(choices),
        size_color_answerable=bool(choices),
        has_confirmed_product_type=bool(product_type_name),
        has_confirmed_material=bool(materials),
    )

    components = []
    description = _display_text(product.description)
    if description:
        components.append(
            ReadyReplyComponent(
                kind=ReadyReplyComponentKind.DESCRIPTION,
                text=f"აღწერა: {description}",
            )
        )
    if product_type_name:
        components.append(
            ReadyReplyComponent(
                kind=ReadyReplyComponentKind.PRODUCT_TYPE,
                text=f"პროდუქტის ტიპი: {product_type_name}.",
            )
        )
    if product.price is not None and product.price > 0:
        components.append(
            ReadyReplyComponent(
                kind=ReadyReplyComponentKind.PRICE,
                text=f"ფასი: {product.price:.2f} {business.default_currency}.",
            )
        )
    if materials:
        components.append(
            ReadyReplyComponent(
                kind=ReadyReplyComponentKind.MATERIAL,
                text="მასალა: "
                + "; ".join(_material_label(material) for material in materials)
                + ".",
            )
        )

    duplicate_groups = _duplicate_choice_groups(choices)
    if choices:
        components.append(
            ReadyReplyComponent(
                kind=ReadyReplyComponentKind.CHOICES,
                text="ზომა, ფერი და მარაგი: "
                + "; ".join(
                    _choice_group_label(group)
                    for group in _choice_groups(choices)
                )
                + ".",
                choice_ids=tuple(choice.choice_id for choice in choices),
            )
        )
        components.append(
            ReadyReplyComponent(
                kind=ReadyReplyComponentKind.AVAILABILITY,
                text=_availability_text(
                    product=product,
                    choices=choices,
                    is_available=is_available,
                ),
                choice_ids=tuple(choice.choice_id for choice in choices),
            )
        )

    seller_notes = list(_missing_seller_notes(coverage))
    for group in duplicate_groups:
        seller_notes.append(
            ReadyReplySellerNote(
                code=ReadyReplyNoteCode.DUPLICATE_CHOICE_AMBIGUITY,
                text=(
                    "ერთნაირი ზომა/ფერი რამდენიმე დამოუკიდებელ რიგშია; "
                    "პასუხში რაოდენობა არ დაჯამებულა."
                ),
                correction_target=CoverageCorrectionTarget.CHOICES,
                choice_ids=tuple(choice.choice_id for choice in group),
            )
        )

    return ReadyReply(
        components=tuple(components),
        seller_notes=tuple(seller_notes),
        choices=choices,
    )


def _display_text(value) -> str:
    return " ".join((value or "").split())


def _normalized_label(value) -> str:
    return _display_text(value).casefold()


def _material_label(material) -> str:
    label = _display_text(material.canonical_material)
    if material.percentage is not None:
        return f"{label} ({material.percentage}%)"
    return label


def _choice_groups(choices):
    groups = []
    group_by_label = {}
    for choice in choices:
        key = (
            _normalized_label(choice.size_name),
            _normalized_label(choice.color_name),
        )
        if key not in group_by_label:
            group_by_label[key] = []
            groups.append(group_by_label[key])
        group_by_label[key].append(choice)
    return tuple(tuple(group) for group in groups)


def _duplicate_choice_groups(choices):
    return tuple(group for group in _choice_groups(choices) if len(group) > 1)


def _choice_group_label(group) -> str:
    choice = group[0]
    identity = f"{choice.size_name} / {choice.color_name}"
    if len(group) > 1:
        return f"{identity} — რაოდენობა დასაზუსტებელია"
    if choice.quantity == 0:
        return f"{identity} — ამოწურულია"
    return f"{identity} — {choice.quantity} ც"


def _availability_text(*, product, choices, is_available) -> str:
    if product.lifecycle != Product.Lifecycle.ACTIVE:
        return "ხელმისაწვდომობა: ამჟამად გასაყიდად აქტიური არ არის."
    if not is_available:
        return "ხელმისაწვდომობა: ამოწურულია."
    if any(choice.quantity == 0 for choice in choices):
        return "ხელმისაწვდომობა: მარაგშია, თუმცა ზოგი არჩევანი ამოწურულია."
    return "ხელმისაწვდომობა: მარაგშია."


def _missing_seller_notes(coverage):
    notes = []
    seen = set()
    for item in coverage.items:
        if item.is_answerable:
            continue
        key = (item.missing_reason, item.correction_target)
        if key in seen:
            continue
        seen.add(key)
        notes.append(
            ReadyReplySellerNote(
                code=ReadyReplyNoteCode(item.missing_reason.value),
                text=_MISSING_NOTE_TEXT[item.missing_reason],
                correction_target=item.correction_target,
            )
        )
    return tuple(notes)
