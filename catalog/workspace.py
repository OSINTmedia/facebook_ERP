"""Read-side boundaries for the seller Product Workspace."""

from dataclasses import dataclass
from urllib.parse import urlencode

from django.db.models import QuerySet
from django.urls import reverse

from businesses.models import Business
from catalog.models import Product


SUPPORTED_PRODUCT_WORKSPACE_QUERY_KEYS: frozenset[str] = frozenset()


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


def product_workspace_products(*, business: Business) -> QuerySet[Product]:
    """Return deterministic Product rows owned by one resolved Business."""

    return Product.objects.filter(business=business).order_by("name", "id")
