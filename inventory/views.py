from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from businesses.selectors import MultipleBusinessesUnsupported, resolve_active_business
from catalog.models import ProductChoice
from catalog.workspace import (
    ProductWorkspaceState,
    build_product_workspace_context,
)
from inventory.mutations import apply_choice_quantity_delta


WORKSPACE_STOCK_RESPONSE_SCOPE = "workspace"


def get_safe_stock_return_url(request):
    candidate = request.POST.get("next") or request.GET.get("next")
    fallback = reverse("catalog:product_list")

    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate

    return fallback


def get_stock_response_scope(request):
    submitted_scopes = request.POST.getlist("response_scope")
    if len(submitted_scopes) > 1:
        raise ValueError("Select one stock response scope.")

    response_scope = submitted_scopes[0] if submitted_scopes else ""
    if response_scope not in {"", WORKSPACE_STOCK_RESPONSE_SCOPE}:
        raise ValueError("Unsupported stock response scope.")
    return response_scope


def get_workspace_stock_state(request):
    submitted_return_urls = request.POST.getlist("next")
    if len(submitted_return_urls) != 1:
        raise ValueError("Workspace stock updates require one return URL.")
    return ProductWorkspaceState.from_return_url(submitted_return_urls[0])


def reject_stock_response_scope(request, error_message):
    if request.htmx:
        return HttpResponse(error_message, status=400)
    messages.error(request, error_message)
    return redirect(reverse("catalog:product_list"))


def render_choice_stock_controls(
    request,
    *,
    choice,
    return_url,
    stock_feedback=None,
    stock_error=None,
):
    choice.refresh_from_db(fields=["quantity", "updated_at"])
    return render(
        request,
        "inventory/_choice_stock_controls.html",
        {
            "choice": choice,
            "return_url": return_url,
            "stock_feedback": stock_feedback,
            "stock_error": stock_error,
        },
    )


def render_workspace_stock_results(
    request,
    *,
    business,
    workspace_state,
    choice,
    is_available=None,
    stock_feedback=None,
    stock_error=None,
):
    context = build_product_workspace_context(
        state=workspace_state,
        business=business,
    )
    choice_is_visible = any(
        card_choice.choice_id == choice.pk
        for card in context["product_cards"]
        for card_choice in card.active_choices
    )
    membership_changed = bool(
        stock_feedback
        and (
            (
                workspace_state.availability_filter == "available"
                and is_available is False
            )
            or (
                workspace_state.availability_filter == "sold_out"
                and is_available is True
            )
        )
    )
    if membership_changed:
        stock_feedback = (
            f"{stock_feedback} The Product moved out of the current results "
            "because its availability changed."
        )
    context.update(
        {
            "workspace_stock_choice_id": choice.pk,
            "workspace_stock_choice_is_visible": choice_is_visible,
            "workspace_stock_feedback": stock_feedback,
            "workspace_stock_error": stock_error,
            "workspace_stock_membership_changed": membership_changed,
        }
    )
    return render(request, "catalog/_product_results.html", context)


class ChoiceStockMutationView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, choice_pk):
        try:
            response_scope = get_stock_response_scope(request)
            workspace_state = (
                get_workspace_stock_state(request)
                if response_scope == WORKSPACE_STOCK_RESPONSE_SCOPE
                else None
            )
        except ValueError as error:
            return reject_stock_response_scope(request, str(error))

        return_url = (
            workspace_state.return_url
            if workspace_state is not None
            else get_safe_stock_return_url(request)
        )

        try:
            business = resolve_active_business(request.user)
        except MultipleBusinessesUnsupported:
            return HttpResponse(
                "Stock updates require one resolved active Business.",
                status=409,
            )

        if business is None:
            return HttpResponse(
                "Stock updates require an active Business.",
                status=409,
            )

        choice = get_object_or_404(
            ProductChoice.objects.select_related("product", "size", "color"),
            pk=choice_pk,
            business=business,
        )
        delta = {"1": 1, "-1": -1}.get(request.POST.get("delta"))
        if delta is None:
            error_message = "Stock adjustment must be +1 or -1."
            if request.htmx:
                if workspace_state is not None:
                    return render_workspace_stock_results(
                        request,
                        business=business,
                        workspace_state=workspace_state,
                        choice=choice,
                        stock_error=error_message,
                    )
                return render_choice_stock_controls(
                    request,
                    choice=choice,
                    return_url=return_url,
                    stock_error=error_message,
                )
            messages.error(request, error_message)
            return redirect(return_url)

        try:
            result = apply_choice_quantity_delta(
                business=business,
                choice=choice,
                actor=request.user,
                delta=delta,
            )
        except ValidationError as error:
            error_message = " ".join(error.messages)
            if request.htmx:
                if workspace_state is not None:
                    return render_workspace_stock_results(
                        request,
                        business=business,
                        workspace_state=workspace_state,
                        choice=choice,
                        stock_error=error_message,
                    )
                return render_choice_stock_controls(
                    request,
                    choice=choice,
                    return_url=return_url,
                    stock_error=error_message,
                )
            messages.error(request, error_message)
            return redirect(return_url)

        feedback = f"Stock updated to {result.choice.quantity}."
        if request.htmx:
            if workspace_state is not None:
                return render_workspace_stock_results(
                    request,
                    business=business,
                    workspace_state=workspace_state,
                    choice=result.choice,
                    is_available=result.is_available,
                    stock_feedback=feedback,
                )
            return render_choice_stock_controls(
                request,
                choice=result.choice,
                return_url=return_url,
                stock_feedback=feedback,
            )
        messages.success(
            request,
            feedback,
        )
        return redirect(return_url)
