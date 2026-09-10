"""Read-side boundaries for the seller Product Workspace."""

from dataclasses import dataclass
from decimal import Decimal
from urllib.parse import urlencode, urlsplit

from django.db.models import Exists, OuterRef, Prefetch, Q, QuerySet, Subquery
from django.http import QueryDict
from django.urls import reverse

from businesses.models import Business
from catalog.forms import ProductWorkspaceSearchForm
from catalog.models import (
    BusinessProductType,
    Product,
    ProductChoice,
    ProductMaterialFact,
    ProductMedia,
)
from catalog.readiness import (
    BuyerQuestion,
    CoverageCorrectionTarget,
    evaluate_buyer_question_coverage,
)
from inventory.availability import compute_availability_from_stock_state
from dashboard.attention import (
    ATTENTION_FILTER_CHOICES,
    attention_group_for_filter,
    build_seller_attention,
)


SUPPORTED_PRODUCT_WORKSPACE_QUERY_KEYS: frozenset[str] = frozenset(
    {"q", "lifecycle", "availability", "attention", "origin"}
)
PRODUCT_WORKSPACE_AVAILABILITY_VALUES: frozenset[str] = frozenset(
    {"available", "sold_out"}
)
PRODUCT_DESCRIPTION_EXCERPT_LENGTH = 160

BUYER_QUESTION_LABELS = {
    BuyerQuestion.PRICE: "Price",
    BuyerQuestion.AVAILABILITY_STOCK: "Stock",
    BuyerQuestion.SIZE_COLOR: "Size and color",
    BuyerQuestion.PRODUCT_TYPE: "Product type",
    BuyerQuestion.MATERIAL: "Material",
}
READINESS_CORRECTIONS = {
    CoverageCorrectionTarget.PRICE: ("Add price", "#id_price"),
    CoverageCorrectionTarget.CHOICES: ("Add active choice", "#choice-section"),
    CoverageCorrectionTarget.CLASSIFICATION: (
        "Confirm product type",
        "#classification-section",
    ),
    CoverageCorrectionTarget.MATERIALS: (
        "Confirm material",
        "#material-section",
    ),
}


@dataclass(frozen=True)
class ProductWorkspaceState:
    """Validated URL state that is safe to carry through Product workflows."""

    query_items: tuple[tuple[str, str], ...] = ()
    search_query: str = ""
    search_requested: bool = False
    search_is_valid: bool = True
    lifecycle_filter: str = ""
    availability_filter: str = ""
    attention_filter: str = ""
    origin: str = ""
    filters_requested: bool = False
    filters_are_valid: bool = True

    @classmethod
    def from_query_params(cls, query_params):
        return cls.from_search_form(ProductWorkspaceSearchForm(query_params))

    @classmethod
    def from_return_url(cls, return_url):
        """Parse one exact canonical local Product Workspace URL."""

        split_url = urlsplit(return_url)
        workspace_path = reverse("catalog:product_list")
        if (
            split_url.scheme
            or split_url.netloc
            or split_url.fragment
            or split_url.path != workspace_path
        ):
            raise ValueError("Unsupported Product Workspace return URL.")

        query_params = QueryDict(split_url.query)
        if any(
            key not in SUPPORTED_PRODUCT_WORKSPACE_QUERY_KEYS
            for key in query_params
        ):
            raise ValueError("Unsupported Product Workspace query state.")

        state = cls.from_query_params(query_params)
        if not state.is_valid or state.return_url != return_url:
            raise ValueError("Invalid Product Workspace query state.")
        return state

    @classmethod
    def from_search_form(cls, search_form):
        search_requested = "q" in search_form.data
        filters_requested = any(
            key in search_form.data
            for key in ("lifecycle", "availability", "attention", "origin")
        )
        search_form.is_valid()
        search_is_valid = "q" not in search_form.errors
        filters_are_valid = not any(
            key in search_form.errors
            for key in ("lifecycle", "availability", "attention", "origin")
        )

        search_query = (
            search_form.cleaned_data.get("q", "") if search_is_valid else ""
        )
        if filters_are_valid:
            lifecycle_filter = search_form.cleaned_data.get("lifecycle", "")
            availability_filter = search_form.cleaned_data.get(
                "availability",
                "",
            )
            attention_filter = search_form.cleaned_data.get("attention", "")
            origin = search_form.cleaned_data.get("origin", "")
        else:
            lifecycle_filter = ""
            availability_filter = ""
            attention_filter = ""
            origin = ""

        query_items = tuple(
            (key, value)
            for key, value in (
                ("q", search_query),
                ("lifecycle", lifecycle_filter),
                ("availability", availability_filter),
                ("attention", attention_filter),
                ("origin", origin),
            )
            if value
        )
        return cls(
            query_items=query_items,
            search_query=search_query,
            search_requested=search_requested,
            search_is_valid=search_is_valid,
            lifecycle_filter=lifecycle_filter,
            availability_filter=availability_filter,
            attention_filter=attention_filter,
            origin=origin,
            filters_requested=filters_requested,
            filters_are_valid=filters_are_valid,
        )

    @property
    def is_valid(self):
        return self.search_is_valid and self.filters_are_valid

    @property
    def has_active_filters(self):
        return bool(
            self.lifecycle_filter
            or self.availability_filter
            or self.attention_filter
        )

    @property
    def active_filter_count(self):
        return sum(
            bool(value)
            for value in (
                self.lifecycle_filter,
                self.availability_filter,
                self.attention_filter,
            )
        )

    @property
    def attention_label(self):
        return dict(ATTENTION_FILTER_CHOICES).get(self.attention_filter, "")

    @property
    def has_dashboard_origin(self):
        return self.origin == "dashboard"

    @property
    def has_active_query(self):
        return bool(self.search_query or self.has_active_filters)

    @property
    def return_url(self):
        return self._url_for(self.query_items)

    @property
    def clear_search_url(self):
        return self._url_for(
            tuple(item for item in self.query_items if item[0] != "q")
        )

    @property
    def clear_filters_url(self):
        return self._url_for(
            tuple(
                item for item in self.query_items if item[0] in {"q", "origin"}
            )
        )

    @property
    def clear_all_url(self):
        return self._url_for(
            tuple(item for item in self.query_items if item[0] == "origin")
        )

    @staticmethod
    def _url_for(query_items):
        base_url = reverse("catalog:product_list")
        if not query_items:
            return base_url
        return f"{base_url}?{urlencode(query_items)}"


@dataclass(frozen=True)
class ProductChoiceCard:
    choice_id: int
    size_name: str
    color_name: str
    quantity: int
    is_attention_target: bool = False


@dataclass(frozen=True)
class ProductCard:
    product_id: int
    name: str
    description_excerpt: str
    primary_media_id: int | None
    price: Decimal | None
    currency: str
    product_type_name: str | None
    lifecycle_label: str
    availability_label: str
    availability_state: str
    is_partially_sold_out: bool
    active_choices: tuple[ProductChoiceCard, ...]
    active_choice_count: int
    active_stock_total: int
    inactive_choice_count: int
    answerable_question_labels: tuple[str, ...]
    missing_question_labels: tuple[str, ...]
    readiness_correction_label: str | None
    readiness_correction_target: str | None
    readiness_correction_fragment: str | None


def build_product_workspace_context(
    *,
    state: ProductWorkspaceState,
    business: Business | None,
):
    """Build the complete server-owned context for one Workspace results view."""

    products = Product.objects.none()
    product_cards = ()
    catalog_has_products = False
    attention_choice_ids = ()

    if business is not None and state.is_valid:
        allowed_product_ids = None
        if state.attention_filter:
            attention = build_seller_attention(business=business)
            attention_group = attention_group_for_filter(
                attention,
                state.attention_filter,
            )
            allowed_product_ids = attention_group.product_ids
            attention_choice_ids = attention_group.choice_ids
        products = product_workspace_products(
            business=business,
            search_query=state.search_query,
            lifecycle_filter=state.lifecycle_filter,
            availability_filter=state.availability_filter,
            allowed_product_ids=allowed_product_ids,
        )
        product_cards = build_product_workspace_cards(
            business=business,
            products=products,
            attention_choice_ids=attention_choice_ids,
        )
        catalog_has_products = bool(product_cards)
        if state.has_active_query and not product_cards:
            catalog_has_products = Product.objects.filter(
                business=business
            ).exists()

    return {
        "product_cards": product_cards,
        "products": products,
        "workspace_search_query": state.search_query,
        "workspace_search_requested": state.search_requested,
        "workspace_search_is_valid": state.search_is_valid,
        "workspace_filters_are_valid": state.filters_are_valid,
        "workspace_query_is_valid": state.is_valid,
        "workspace_lifecycle_filter": state.lifecycle_filter,
        "workspace_availability_filter": state.availability_filter,
        "workspace_attention_filter": state.attention_filter,
        "workspace_attention_label": state.attention_label,
        "workspace_attention_choice_ids": attention_choice_ids,
        "workspace_has_active_filters": state.has_active_filters,
        "workspace_active_filter_count": state.active_filter_count,
        "workspace_back_to_dashboard_url": (
            reverse("shell_home") if state.has_dashboard_origin else ""
        ),
        "workspace_result_count": len(product_cards),
        "catalog_has_products": catalog_has_products,
        "workspace_return_url": state.return_url,
        "workspace_clear_search_url": state.clear_search_url,
        "workspace_clear_filters_url": state.clear_filters_url,
        "workspace_clear_all_url": state.clear_all_url,
    }


def product_workspace_products(
    *,
    business: Business,
    search_query: str = "",
    lifecycle_filter: str = "",
    availability_filter: str = "",
    allowed_product_ids=None,
) -> QuerySet[Product]:
    """Return deterministic Product rows owned by one resolved Business."""

    if lifecycle_filter not in {"", *Product.Lifecycle.values}:
        raise ValueError("Unsupported Product lifecycle filter.")
    if availability_filter not in {"", *PRODUCT_WORKSPACE_AVAILABILITY_VALUES}:
        raise ValueError("Unsupported Product availability filter.")

    product_type_name = BusinessProductType.objects.filter(
        business=business,
        pk=OuterRef("product_type_id"),
    ).values("name")[:1]
    primary_media_id = ProductMedia.objects.filter(
        business=business,
        product__business=business,
        product_id=OuterRef("pk"),
    ).values("pk")[:1]
    confirmed_material_fact = ProductMaterialFact.objects.filter(
        business=business,
        product__business=business,
        product_id=OuterRef("pk"),
        confirmation_state=ProductMaterialFact.ConfirmationState.CONFIRMED,
    )
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
    if allowed_product_ids is not None:
        products = products.filter(pk__in=allowed_product_ids)
    if lifecycle_filter:
        products = products.filter(lifecycle=lifecycle_filter)
    for token in search_query.split():
        products = products.filter(
            _product_search_token_filter(business=business, token=token)
        )
    if search_query:
        products = products.distinct()

    if availability_filter:
        positive_active_choice = ProductChoice.objects.filter(
            business=business,
            product__business=business,
            product_id=OuterRef("pk"),
            size__business=business,
            color__business=business,
            is_active=True,
            quantity__gt=0,
        )
        products = products.annotate(
            workspace_has_positive_active_choice=Exists(
                positive_active_choice
            )
        ).filter(
            lifecycle=Product.Lifecycle.ACTIVE,
            workspace_has_positive_active_choice=(
                availability_filter == "available"
            ),
        )

    return (
        products
        .annotate(
            workspace_product_type_name=Subquery(product_type_name),
            workspace_primary_media_id=Subquery(primary_media_id),
            workspace_has_confirmed_material=Exists(confirmed_material_fact),
        )
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
    attention_choice_ids=(),
) -> tuple[ProductCard, ...]:
    """Build immutable card state from the Business-scoped prefetched read model."""

    if business is None or business.pk is None:
        raise ValueError("An existing Business is required.")

    attention_choice_ids = frozenset(attention_choice_ids)
    return tuple(
        _build_product_card(
            business=business,
            product=product,
            attention_choice_ids=attention_choice_ids,
        )
        for product in products
    )


def _build_product_card(
    *,
    business: Business,
    product: Product,
    attention_choice_ids=frozenset(),
) -> ProductCard:
    if product.business_id != business.pk:
        raise ValueError("Product must belong to the active Business.")
    if (
        not hasattr(product, "workspace_choices")
        or not hasattr(product, "workspace_product_type_name")
        or not hasattr(product, "workspace_primary_media_id")
        or not hasattr(product, "workspace_has_confirmed_material")
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
            is_attention_target=choice.pk in attention_choice_ids,
        )
        for choice in active_choice_rows
    )
    has_positive_active_choice = any(
        choice.quantity > 0 for choice in active_choice_rows
    )
    has_zero_active_choice = any(
        choice.quantity == 0 for choice in active_choice_rows
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

    coverage = evaluate_buyer_question_coverage(
        has_confirmed_price=product.price is not None and product.price > 0,
        availability_stock_answerable=bool(active_choice_rows),
        size_color_answerable=bool(active_choice_rows),
        has_confirmed_product_type=bool(product.workspace_product_type_name),
        has_confirmed_material=product.workspace_has_confirmed_material,
    )
    answerable_question_labels = tuple(
        BUYER_QUESTION_LABELS[item.question]
        for item in coverage.items
        if item.is_answerable
    )
    missing_items = tuple(item for item in coverage.items if not item.is_answerable)
    missing_question_labels = tuple(
        BUYER_QUESTION_LABELS[item.question] for item in missing_items
    )
    next_correction = missing_items[0] if missing_items else None
    correction_label = None
    correction_fragment = None
    if next_correction is not None:
        correction_label, correction_fragment = READINESS_CORRECTIONS[
            next_correction.correction_target
        ]

    description_excerpt = _description_excerpt(product.description)
    if _name_is_derived_from_description(
        name=product.name,
        description=product.description,
    ):
        description_excerpt = ""

    return ProductCard(
        product_id=product.pk,
        name=product.name,
        description_excerpt=description_excerpt,
        primary_media_id=product.workspace_primary_media_id,
        price=product.price,
        currency=business.default_currency,
        product_type_name=product.workspace_product_type_name,
        lifecycle_label=product.get_lifecycle_display(),
        availability_label=availability_label,
        availability_state=availability_state,
        is_partially_sold_out=(
            product.lifecycle == Product.Lifecycle.ACTIVE
            and has_positive_active_choice
            and has_zero_active_choice
        ),
        active_choices=active_choices,
        active_choice_count=len(active_choices),
        active_stock_total=sum(choice.quantity for choice in active_choice_rows),
        inactive_choice_count=len(choices) - len(active_choice_rows),
        answerable_question_labels=answerable_question_labels,
        missing_question_labels=missing_question_labels,
        readiness_correction_label=correction_label,
        readiness_correction_target=(
            next_correction.correction_target if next_correction else None
        ),
        readiness_correction_fragment=correction_fragment,
    )


def _description_excerpt(description: str) -> str:
    description = description.strip()
    if len(description) <= PRODUCT_DESCRIPTION_EXCERPT_LENGTH:
        return description

    return (
        description[: PRODUCT_DESCRIPTION_EXCERPT_LENGTH - 1].rstrip()
        + "…"
    )


def _name_is_derived_from_description(*, name: str, description: str) -> bool:
    normalized_description = " ".join(description.split())
    name_max_length = Product._meta.get_field("name").max_length
    return name == normalized_description[:name_max_length]
