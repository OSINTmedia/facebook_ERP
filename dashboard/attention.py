"""Business-scoped seller attention signals from shared catalog truth."""

from dataclasses import dataclass

from django.conf import settings
from django.db.models import Exists, OuterRef

from catalog.models import (
    BusinessProductType,
    Product,
    ProductChoice,
    ProductMaterialFact,
)
from catalog.readiness import evaluate_buyer_question_coverage
from inventory.availability import compute_availability_from_stock_state


DEFAULT_ATTENTION_LIST_LIMIT = 5
DAILY_PRODUCT_LIFECYCLES = (
    Product.Lifecycle.DRAFT,
    Product.Lifecycle.ACTIVE,
)
ATTENTION_FILTER_CHOICES = (
    ("", "All attention states"),
    ("missing_information", "Missing information"),
    ("low_stock", "Low stock"),
    ("sold_out", "Sold out / restock"),
    ("partial_stock", "Partially sold out"),
)
ATTENTION_FILTER_GROUPS = {
    "missing_information": "missing_information_products",
    "low_stock": "low_stock_choices",
    "sold_out": "sold_out_products",
    "partial_stock": "partially_sold_out_choices",
}


@dataclass(frozen=True)
class AttentionGroup:
    count: int
    items: tuple
    product_ids: tuple[int, ...]
    choice_ids: tuple[int, ...]


@dataclass(frozen=True)
class SellerAttention:
    sold_out_products: AttentionGroup
    partially_sold_out_choices: AttentionGroup
    low_stock_choices: AttentionGroup
    missing_information_products: AttentionGroup
    empty_catalog: bool
    low_stock_threshold: int


def build_seller_attention(
    *,
    business,
    low_stock_threshold=None,
    list_limit=DEFAULT_ATTENTION_LIST_LIMIT,
) -> SellerAttention:
    """Return bounded seller-attention lists with exact deterministic counts."""

    if business is None or business.pk is None:
        raise ValueError("An existing Business is required.")

    threshold = (
        settings.DASHBOARD_LOW_STOCK_THRESHOLD
        if low_stock_threshold is None
        else low_stock_threshold
    )
    if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 1:
        raise ValueError("Low-stock threshold must be a positive integer.")
    if isinstance(list_limit, bool) or not isinstance(list_limit, int) or list_limit < 0:
        raise ValueError("Attention list limit must be a nonnegative integer.")

    confirmed_material = ProductMaterialFact.objects.filter(
        business=business,
        product_id=OuterRef("pk"),
        confirmation_state=ProductMaterialFact.ConfirmationState.CONFIRMED,
    )
    scoped_product_type = BusinessProductType.objects.filter(
        business=business,
        pk=OuterRef("product_type_id"),
    )
    products = tuple(
        Product.objects.filter(
            business=business,
            lifecycle__in=DAILY_PRODUCT_LIFECYCLES,
        )
        .annotate(
            attention_has_confirmed_material=Exists(confirmed_material),
            attention_has_scoped_product_type=Exists(scoped_product_type),
        )
        .order_by("name", "id")
    )

    active_choices = tuple(
        ProductChoice.objects.filter(
            business=business,
            product__business=business,
            product__lifecycle__in=DAILY_PRODUCT_LIFECYCLES,
            is_active=True,
        )
        .select_related("product", "size", "color")
        .order_by("product__name", "product_id", "id")
    )
    choices_by_product = {}
    for choice in active_choices:
        choices_by_product.setdefault(choice.product_id, []).append(choice)

    sold_out_products = []
    partially_sold_out_choices = []
    low_stock_choices = []
    missing_information_products = []

    for product in products:
        product_choices = choices_by_product.get(product.pk, ())
        has_active_choice = bool(product_choices)
        has_positive_active_choice = any(
            choice.quantity > 0 for choice in product_choices
        )
        is_available = compute_availability_from_stock_state(
            product_lifecycle=product.lifecycle,
            has_positive_active_choice=has_positive_active_choice,
        )

        if product.lifecycle == Product.Lifecycle.ACTIVE:
            if has_active_choice and not is_available:
                sold_out_products.append(product)
            if has_positive_active_choice:
                partially_sold_out_choices.extend(
                    choice for choice in product_choices if choice.quantity == 0
                )
            low_stock_choices.extend(
                choice
                for choice in product_choices
                if 0 < choice.quantity <= threshold
            )

        coverage = evaluate_buyer_question_coverage(
            has_confirmed_price=product.price is not None and product.price > 0,
            availability_stock_answerable=has_active_choice,
            size_color_answerable=has_active_choice,
            has_confirmed_product_type=product.attention_has_scoped_product_type,
            has_confirmed_material=product.attention_has_confirmed_material,
        )
        if any(not item.is_answerable for item in coverage.items):
            missing_information_products.append(product)

    return SellerAttention(
        sold_out_products=_attention_group(sold_out_products, list_limit),
        partially_sold_out_choices=_attention_group(
            partially_sold_out_choices,
            list_limit,
        ),
        low_stock_choices=_attention_group(low_stock_choices, list_limit),
        missing_information_products=_attention_group(
            missing_information_products,
            list_limit,
        ),
        empty_catalog=not products,
        low_stock_threshold=threshold,
    )


def _attention_group(items, list_limit) -> AttentionGroup:
    product_ids = tuple(
        dict.fromkeys(
            item.product_id if isinstance(item, ProductChoice) else item.pk
            for item in items
        )
    )
    choice_ids = tuple(
        item.pk for item in items if isinstance(item, ProductChoice)
    )
    return AttentionGroup(
        count=len(items),
        items=tuple(items[:list_limit]),
        product_ids=product_ids,
        choice_ids=choice_ids,
    )


def attention_group_for_filter(attention, attention_filter) -> AttentionGroup:
    """Resolve one approved Workspace drilldown to shared attention truth."""

    try:
        group_name = ATTENTION_FILTER_GROUPS[attention_filter]
    except KeyError as exc:
        raise ValueError("Unsupported attention filter.") from exc
    return getattr(attention, group_name)
