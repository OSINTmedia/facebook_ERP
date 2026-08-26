"""Read-side boundaries for the seller Product Workspace."""

from dataclasses import dataclass
from urllib.parse import urlencode

from django.db.models import OuterRef, Prefetch, QuerySet, Subquery
from django.urls import reverse

from businesses.models import Business
from catalog.models import BusinessProductType, Product, ProductChoice
from inventory.availability import compute_availability_from_stock_state


SUPPORTED_PRODUCT_WORKSPACE_QUERY_KEYS: frozenset[str] = frozenset()
PRODUCT_DESCRIPTION_EXCERPT_LENGTH = 160


@dataclass(frozen=True)
class ProductWorkspaceState:
    """Validated URL state that is safe to carry through Product workflows."""

    query_items: tuple[tuple[str, str], ...] = ()

    @classmethod
    def from_query_params(cls, query_params):
        query_items = tuple(
            (key, value)
            for key in sorted(SUPPORTED_PRODUCT_WORKSPACE_QUERY_KEYS)
            if (value := query_params.get(key, "").strip())
        )
        return cls(query_items=query_items)

    @property
    def return_url(self):
        base_url = reverse("catalog:product_list")
        if not self.query_items:
            return base_url
        return f"{base_url}?{urlencode(self.query_items)}"


@dataclass(frozen=True)
class ProductChoiceCard:
    choice_id: int
    size_name: str
    color_name: str
    quantity: int


@dataclass(frozen=True)
class ProductCard:
    product_id: int
    name: str
    description_excerpt: str
    product_type_name: str | None
    lifecycle_label: str
    availability_label: str
    availability_state: str
    active_choices: tuple[ProductChoiceCard, ...]
    active_choice_count: int
    active_stock_total: int
    inactive_choice_count: int


def product_workspace_products(*, business: Business) -> QuerySet[Product]:
    """Return deterministic Product rows owned by one resolved Business."""

    product_type_name = BusinessProductType.objects.filter(
        business=business,
        pk=OuterRef("product_type_id"),
    ).values("name")[:1]
    choices = (
        ProductChoice.objects.filter(
            business=business,
            product__business=business,
            size__business=business,
            color__business=business,
        )
        .select_related("size", "color")
        .order_by("product_id", "size_id", "color_id", "id")
    )

    return (
        Product.objects.filter(business=business)
        .annotate(workspace_product_type_name=Subquery(product_type_name))
        .prefetch_related(
            Prefetch(
                "choices",
                queryset=choices,
                to_attr="workspace_choices",
            )
        )
        .order_by("name", "id")
    )


def build_product_workspace_cards(
    *,
    business: Business,
    products,
) -> tuple[ProductCard, ...]:
    """Build immutable card state from the Business-scoped prefetched read model."""

    if business is None or business.pk is None:
        raise ValueError("An existing Business is required.")

    return tuple(
        _build_product_card(business=business, product=product)
        for product in products
    )


def _build_product_card(*, business: Business, product: Product) -> ProductCard:
    if product.business_id != business.pk:
        raise ValueError("Product must belong to the active Business.")
    if not hasattr(product, "workspace_choices") or not hasattr(
        product,
        "workspace_product_type_name",
    ):
        raise ValueError("Product must come from the Product Workspace query.")

    choices = tuple(product.workspace_choices)
    active_choice_rows = tuple(choice for choice in choices if choice.is_active)
    active_choices = tuple(
        ProductChoiceCard(
            choice_id=choice.pk,
            size_name=choice.size.name,
            color_name=choice.color.name,
            quantity=choice.quantity,
        )
        for choice in active_choice_rows
    )
    has_positive_active_choice = any(
        choice.quantity > 0 for choice in active_choice_rows
    )
    is_available = compute_availability_from_stock_state(
        product_lifecycle=product.lifecycle,
        has_positive_active_choice=has_positive_active_choice,
    )

    if product.lifecycle != Product.Lifecycle.ACTIVE:
        availability_label = "Not sellable"
        availability_state = "not-sellable"
    elif is_available:
        availability_label = "Available"
        availability_state = "available"
    else:
        availability_label = "Sold out"
        availability_state = "sold-out"

    return ProductCard(
        product_id=product.pk,
        name=product.name,
        description_excerpt=_description_excerpt(product.description),
        product_type_name=product.workspace_product_type_name,
        lifecycle_label=product.get_lifecycle_display(),
        availability_label=availability_label,
        availability_state=availability_state,
        active_choices=active_choices,
        active_choice_count=len(active_choices),
        active_stock_total=sum(choice.quantity for choice in active_choice_rows),
        inactive_choice_count=len(choices) - len(active_choice_rows),
    )


def _description_excerpt(description: str) -> str:
    description = description.strip()
    if len(description) <= PRODUCT_DESCRIPTION_EXCERPT_LENGTH:
        return description

    return (
        description[: PRODUCT_DESCRIPTION_EXCERPT_LENGTH - 1].rstrip()
        + "…"
    )
