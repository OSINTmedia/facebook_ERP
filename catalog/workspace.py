"""Read-side boundaries for the seller Product Workspace."""

from dataclasses import dataclass
from urllib.parse import urlencode

from django.db.models import OuterRef, Prefetch, Q, QuerySet, Subquery
from django.urls import reverse

from businesses.models import Business
from catalog.forms import ProductWorkspaceSearchForm
from catalog.models import (
    BusinessProductType,
    Product,
    ProductChoice,
    ProductMaterialFact,
)
from inventory.availability import compute_availability_from_stock_state


SUPPORTED_PRODUCT_WORKSPACE_QUERY_KEYS: frozenset[str] = frozenset({"q"})
PRODUCT_DESCRIPTION_EXCERPT_LENGTH = 160


@dataclass(frozen=True)
class ProductWorkspaceState:
    """Validated URL state that is safe to carry through Product workflows."""

    query_items: tuple[tuple[str, str], ...] = ()
    search_query: str = ""
    search_requested: bool = False
    search_is_valid: bool = True

    @classmethod
    def from_query_params(cls, query_params):
        return cls.from_search_form(ProductWorkspaceSearchForm(query_params))

    @classmethod
    def from_search_form(cls, search_form):
        search_requested = "q" in search_form.data
        if not search_form.is_valid():
            return cls(
                search_requested=search_requested,
                search_is_valid=False,
            )

        search_query = search_form.cleaned_data["q"]
        query_items = (("q", search_query),) if search_query else ()
        return cls(
            query_items=query_items,
            search_query=search_query,
            search_requested=search_requested,
        )

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


def product_workspace_products(
    *,
    business: Business,
    search_query: str = "",
) -> QuerySet[Product]:
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

    products = Product.objects.filter(business=business)
    for token in search_query.split():
        products = products.filter(
            _product_search_token_filter(business=business, token=token)
        )
    if search_query:
        products = products.distinct()

    return (
        products
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


def _product_search_token_filter(*, business: Business, token: str) -> Q:
    product_type_match = Q(product_type__business=business) & (
        Q(product_type__name__icontains=token)
        | (
            Q(product_type__aliases__business=business)
            & Q(product_type__aliases__alias__icontains=token)
        )
    )
    tag_match = (
        Q(tag_links__business=business)
        & Q(tag_links__tag__business=business)
        & (
            Q(tag_links__tag__name__icontains=token)
            | (
                Q(tag_links__tag__aliases__business=business)
                & Q(tag_links__tag__aliases__alias__icontains=token)
            )
        )
    )
    choice_scope = (
        Q(choices__business=business)
        & Q(choices__size__business=business)
        & Q(choices__color__business=business)
    )
    size_match = (
        choice_scope
        & (
            Q(choices__size__name__icontains=token)
            | (
                Q(choices__size__aliases__business=business)
                & Q(choices__size__aliases__alias__icontains=token)
            )
        )
    )
    color_match = (
        choice_scope
        & (
            Q(choices__color__name__icontains=token)
            | (
                Q(choices__color__aliases__business=business)
                & Q(choices__color__aliases__alias__icontains=token)
            )
        )
    )
    material_match = (
        Q(material_facts__business=business)
        & Q(
            material_facts__confirmation_state=(
                ProductMaterialFact.ConfirmationState.CONFIRMED
            )
        )
        & (
            Q(material_facts__canonical_material__icontains=token)
            | Q(material_facts__original_text__icontains=token)
        )
    )

    return (
        Q(name__icontains=token)
        | Q(description__icontains=token)
        | product_type_match
        | tag_match
        | size_match
        | color_match
        | material_match
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
