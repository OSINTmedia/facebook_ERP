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
from inventory.mutations import apply_choice_quantity_delta


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


class ChoiceStockMutationView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, choice_pk):
        return_url = get_safe_stock_return_url(request)

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
