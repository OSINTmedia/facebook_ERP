"""Read-side helpers for seller-owned business scope."""

from django.http import Http404

from businesses.models import Business


class MultipleBusinessesUnsupported(RuntimeError):
    """Raised when a seller has multiple businesses but no switcher policy exists."""


def businesses_owned_by(user):
    """Return only businesses owned by an authenticated seller."""
    if not getattr(user, "is_authenticated", False):
        return Business.objects.none()

    return Business.objects.filter(owner=user).order_by("created_at", "id")


def resolve_active_business(user):
    """Return the seller's only business, or None when no workspace exists yet."""
    businesses = list(businesses_owned_by(user)[:2])

    if not businesses:
        return None
    if len(businesses) > 1:
        raise MultipleBusinessesUnsupported(
            "Multiple businesses require an approved active-business policy."
        )

    return businesses[0]


def get_owned_business_or_404(user, business_id):
    """Return one owned business by id without leaking another seller's workspace."""
    try:
        return businesses_owned_by(user).get(pk=business_id)
    except Business.DoesNotExist as exc:
        raise Http404("Business not found.") from exc
