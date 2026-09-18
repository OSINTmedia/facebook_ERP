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
from inventory.mutations import apply_choice_quantity_delta, set_choice_quantity


WORKSPACE_STOCK_RESPONSE_SCOPE = "workspace"


def stock_error_for_seller(error):
    message = " ".join(error.messages)
    translations = {
        "Choice quantity cannot be negative.": "მარაგი ნულზე ნაკლები ვერ იქნება.",
        "Archived Product stock cannot be changed.": "დაარქივებული პროდუქტის მარაგი ვერ შეიცვლება.",
        "Choose exactly one stock action.": "აირჩიეთ მარაგის მხოლოდ ერთი მოქმედება.",
        "Stock adjustment must be +1 or -1.": "მარაგის ცვლილება უნდა იყოს +1 ან -1.",
        "Set quantity must be a nonnegative integer.": "რაოდენობა უნდა იყოს მთელი რიცხვი და არ უნდა იყოს უარყოფითი.",
    }
    if message.startswith("Choice quantity cannot exceed "):
        maximum = message.removeprefix("Choice quantity cannot exceed ").removesuffix(".")
        return f"მარაგი {maximum}-ზე მეტი ვერ იქნება."
    return translations.get(message, message)


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
    stock_action=None,
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
            f"{stock_feedback} ხელმისაწვდომობის შეცვლის გამო პროდუქტი მიმდინარე "
            "შედეგებიდან გადავიდა."
        )
    context.update(
        {
            "workspace_stock_choice_id": choice.pk,
            "workspace_stock_choice_is_visible": choice_is_visible,
            "workspace_stock_feedback": stock_feedback,
            "workspace_stock_error": stock_error,
            "workspace_stock_action": stock_action,
            "workspace_stock_membership_changed": membership_changed,
        }
    )
    response = render(request, "catalog/_product_results.html", context)
    if context["workspace_page_recovered"]:
        response["HX-Replace-Url"] = context["workspace_return_url"]
    return response


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
                "მარაგის შესაცვლელად უნდა არჩეული იყოს ერთი აქტიური ბიზნესი.",
                status=409,
            )

        if business is None:
            return HttpResponse(
                "მარაგის შესაცვლელად აქტიური ბიზნესია საჭირო.",
                status=409,
            )

        choice = get_object_or_404(
            ProductChoice.objects.select_related("product", "size", "color"),
            pk=choice_pk,
            business=business,
        )
        stock_action = None
        try:
            submitted_deltas = request.POST.getlist("delta")
            submitted_quantities = request.POST.getlist("quantity")
            if (
                len(submitted_deltas) + len(submitted_quantities) != 1
                or bool(submitted_deltas) == bool(submitted_quantities)
            ):
                raise ValidationError("Choose exactly one stock action.")

            if submitted_deltas:
                stock_action = "delta"
                delta = {"1": 1, "-1": -1}.get(submitted_deltas[0])
                if delta is None:
                    raise ValidationError("Stock adjustment must be +1 or -1.")
                result = apply_choice_quantity_delta(
                    business=business,
                    choice=choice,
                    actor=request.user,
                    delta=delta,
                )
            else:
                stock_action = "set"
                quantity_text = submitted_quantities[0]
                if not quantity_text.isascii() or not quantity_text.isdecimal():
                    raise ValidationError(
                        "Set quantity must be a nonnegative integer."
                    )
                try:
                    quantity = int(quantity_text)
                except ValueError as error:
                    raise ValidationError(
                        "Set quantity must be a nonnegative integer."
                    ) from error
                result = set_choice_quantity(
                    business=business,
                    choice=choice,
                    actor=request.user,
                    quantity=quantity,
                )
        except ValidationError as error:
            error_message = stock_error_for_seller(error)
            if request.htmx:
                if workspace_state is not None:
                    return render_workspace_stock_results(
                        request,
                        business=business,
                        workspace_state=workspace_state,
                        choice=choice,
                        stock_error=error_message,
                        stock_action=stock_action,
                    )
                return render_choice_stock_controls(
                    request,
                    choice=choice,
                    return_url=return_url,
                    stock_error=error_message,
                )
            messages.error(request, error_message)
            return redirect(return_url)

        if stock_action == "set":
            feedback = (
                f"მარაგი განისაზღვრა: {result.choice.quantity}."
                if result.adjustment is not None
                else (
                    f"მარაგი უკვე {result.choice.quantity}-ია; "
                    "ცვლილება არ ჩაწერილა."
                )
            )
        else:
            feedback = f"მარაგი განახლდა: {result.choice.quantity}."
        if request.htmx:
            if workspace_state is not None:
                return render_workspace_stock_results(
                    request,
                    business=business,
                    workspace_state=workspace_state,
                    choice=result.choice,
                    is_available=result.is_available,
                    stock_feedback=feedback,
                    stock_action=stock_action,
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
