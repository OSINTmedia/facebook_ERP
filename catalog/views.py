from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView

from businesses.selectors import MultipleBusinessesUnsupported, resolve_active_business
from catalog.forms import ChoiceVocabularyForm
from catalog.models import Product
from catalog.product_bundles import ProductBundle
from catalog.recognition import recognize_product_preview_for_business
from catalog.vocabulary import (
    COLOR_VOCABULARY,
    SIZE_VOCABULARY,
    create_choice_vocabulary_entry,
)


RECOGNITION_PREVIEW_INTENT = "preview_recognition"
ADD_SIZE_VOCABULARY_INTENT = "add_size_vocabulary"
ADD_COLOR_VOCABULARY_INTENT = "add_color_vocabulary"


def get_safe_product_return_url(request):
    candidate = request.POST.get("next") or request.GET.get("next")
    fallback = reverse("catalog:product_list")

    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate

    return fallback


class ProductListView(LoginRequiredMixin, TemplateView):
    template_name = "catalog/product_list.html"

    def get(self, request, *args, **kwargs):
        self.business_policy_blocked = False
        self.active_business = None

        try:
            self.active_business = resolve_active_business(request.user)
        except MultipleBusinessesUnsupported:
            self.business_policy_blocked = True
            context = self.get_context_data()
            return self.render_to_response(context, status=409)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.none()

        if self.active_business is not None:
            products = Product.objects.filter(business=self.active_business)

        context.update(
            {
                "active_business": self.active_business,
                "business_policy_blocked": self.business_policy_blocked,
                "current_nav": "products",
                "products": products,
            }
        )
        return context


class ProductMutationBusinessMixin(LoginRequiredMixin):
    template_name = "catalog/product_form.html"

    def resolve_business(self, request):
        self.business_policy_blocked = False
        self.active_business = None

        try:
            self.active_business = resolve_active_business(request.user)
        except MultipleBusinessesUnsupported:
            self.business_policy_blocked = True

    def base_context(self, request, **context):
        context.setdefault("active_business", self.active_business)
        context.setdefault("business_policy_blocked", self.business_policy_blocked)
        context.setdefault("current_nav", "products")
        context.setdefault("page_title", "Product")
        context.setdefault("return_url", get_safe_product_return_url(request))
        return context

    def render_business_blocked(self, request):
        return render(
            request,
            self.template_name,
            self.base_context(request),
            status=409,
        )

    def bundle_context(
        self,
        request,
        bundle,
        *,
        preview_requested=False,
        show_form_errors=True,
        **context,
    ):
        recognition_preview = None
        if bundle is not None and self.active_business is not None:
            description = bundle.product_form["description"].value()
            recognition_preview = recognize_product_preview_for_business(
                description,
                self.active_business,
            )

        context.setdefault(
            "size_vocabulary_form",
            ChoiceVocabularyForm(kind=SIZE_VOCABULARY, prefix="size-vocabulary"),
        )
        context.setdefault(
            "color_vocabulary_form",
            ChoiceVocabularyForm(kind=COLOR_VOCABULARY, prefix="color-vocabulary"),
        )

        return self.base_context(
            request,
            form=bundle.product_form if bundle is not None else None,
            choice_formset=bundle.choice_formset if bundle is not None else None,
            preview_requested=preview_requested,
            recognition_preview=recognition_preview,
            show_form_errors=show_form_errors,
            **context,
        )

    def is_recognition_preview_request(self, request):
        return request.POST.get("intent") == RECOGNITION_PREVIEW_INTENT

    def is_vocabulary_request(self, request):
        return request.POST.get("intent") in {
            ADD_SIZE_VOCABULARY_INTENT,
            ADD_COLOR_VOCABULARY_INTENT,
        }

    def handle_vocabulary_request(self, request, bundle, **context):
        intent = request.POST.get("intent")
        kind = (
            SIZE_VOCABULARY
            if intent == ADD_SIZE_VOCABULARY_INTENT
            else COLOR_VOCABULARY
        )
        size_form = ChoiceVocabularyForm(
            kind=SIZE_VOCABULARY,
            prefix="size-vocabulary",
        )
        color_form = ChoiceVocabularyForm(
            kind=COLOR_VOCABULARY,
            prefix="color-vocabulary",
        )
        vocabulary_form = ChoiceVocabularyForm(
            request.POST,
            kind=kind,
            prefix=f"{kind}-vocabulary",
        )
        if kind == SIZE_VOCABULARY:
            size_form = vocabulary_form
        else:
            color_form = vocabulary_form

        vocabulary_feedback = None
        if vocabulary_form.is_valid():
            try:
                canonical = create_choice_vocabulary_entry(
                    business=self.active_business,
                    kind=kind,
                    name=vocabulary_form.cleaned_data["name"],
                    aliases=vocabulary_form.cleaned_data["aliases"],
                )
            except ValidationError as error:
                self.add_vocabulary_errors(vocabulary_form, error)
            else:
                label = "Size" if kind == SIZE_VOCABULARY else "Color"
                vocabulary_feedback = f'{label} "{canonical.name}" saved.'
                if kind == SIZE_VOCABULARY:
                    size_form = ChoiceVocabularyForm(
                        kind=SIZE_VOCABULARY,
                        prefix="size-vocabulary",
                    )
                else:
                    color_form = ChoiceVocabularyForm(
                        kind=COLOR_VOCABULARY,
                        prefix="color-vocabulary",
                    )
                bundle = ProductBundle(
                    business=self.active_business,
                    data=request.POST,
                    instance=bundle.product,
                )

        rendered_context = self.bundle_context(
            request,
            bundle,
            show_form_errors=False,
            size_vocabulary_form=size_form,
            color_vocabulary_form=color_form,
            vocabulary_feedback=vocabulary_feedback,
            **context,
        )
        return render(
            request,
            (
                "catalog/_choice_section.html"
                if request.htmx
                else self.template_name
            ),
            rendered_context,
        )

    @staticmethod
    def add_vocabulary_errors(form, error):
        if hasattr(error, "message_dict"):
            for field_name, messages_for_field in error.message_dict.items():
                target = field_name if field_name in form.fields else None
                if field_name == NON_FIELD_ERRORS:
                    target = None
                for message in messages_for_field:
                    form.add_error(target, message)
            return

        for message in error.messages:
            form.add_error(None, message)


class ProductCreateView(ProductMutationBusinessMixin, View):
    def get(self, request, *args, **kwargs):
        self.resolve_business(request)
        if self.business_policy_blocked:
            return self.render_business_blocked(request)

        bundle = None
        if self.active_business is not None:
            bundle = ProductBundle(business=self.active_business)

        return render(
            request,
            self.template_name,
            self.bundle_context(
                request,
                bundle,
                page_title="Add product",
                submit_label="Create product",
            ),
        )

    def post(self, request, *args, **kwargs):
        self.resolve_business(request)
        if self.business_policy_blocked or self.active_business is None:
            return self.render_business_blocked(request)

        bundle = ProductBundle(
            business=self.active_business,
            data=request.POST,
        )
        if self.is_recognition_preview_request(request):
            context = self.bundle_context(
                request,
                bundle,
                preview_requested=True,
                show_form_errors=False,
                page_title="Add product",
                submit_label="Create product",
            )
            return render(
                request,
                (
                    "catalog/_recognition_preview.html"
                    if request.htmx
                    else self.template_name
                ),
                context,
            )

        if self.is_vocabulary_request(request):
            return self.handle_vocabulary_request(
                request,
                bundle,
                page_title="Add product",
                submit_label="Create product",
            )

        if bundle.is_valid():
            bundle.save()
            messages.success(request, "Product created.")
            return redirect(get_safe_product_return_url(request))

        return render(
            request,
            self.template_name,
            self.bundle_context(
                request,
                bundle,
                page_title="Add product",
                submit_label="Create product",
            ),
        )


class ProductUpdateView(ProductMutationBusinessMixin, View):
    def get_product(self):
        if self.active_business is None:
            raise Http404("Product not found.")

        try:
            return Product.objects.get(
                business=self.active_business,
                pk=self.kwargs["pk"],
            )
        except Product.DoesNotExist as exc:
            raise Http404("Product not found.") from exc

    def get(self, request, *args, **kwargs):
        self.kwargs = kwargs
        self.resolve_business(request)
        if self.business_policy_blocked:
            return self.render_business_blocked(request)

        product = self.get_product()
        bundle = ProductBundle(
            business=self.active_business,
            instance=product,
        )
        return render(
            request,
            self.template_name,
            self.bundle_context(
                request,
                bundle,
                page_title=f"Edit {product.name}",
                product=product,
                submit_label="Save changes",
            ),
        )

    def post(self, request, *args, **kwargs):
        self.kwargs = kwargs
        self.resolve_business(request)
        if self.business_policy_blocked:
            return self.render_business_blocked(request)

        product = self.get_product()
        bundle = ProductBundle(
            business=self.active_business,
            data=request.POST,
            instance=product,
        )
        if self.is_recognition_preview_request(request):
            context = self.bundle_context(
                request,
                bundle,
                preview_requested=True,
                show_form_errors=False,
                page_title=f"Edit {product.name}",
                product=product,
                submit_label="Save changes",
            )
            return render(
                request,
                (
                    "catalog/_recognition_preview.html"
                    if request.htmx
                    else self.template_name
                ),
                context,
            )

        if self.is_vocabulary_request(request):
            return self.handle_vocabulary_request(
                request,
                bundle,
                page_title=f"Edit {product.name}",
                product=product,
                submit_label="Save changes",
            )

        if bundle.is_valid():
            bundle.save()
            messages.success(request, "Product updated.")
            return redirect(get_safe_product_return_url(request))

        return render(
            request,
            self.template_name,
            self.bundle_context(
                request,
                bundle,
                page_title=f"Edit {product.name}",
                product=product,
                submit_label="Save changes",
            ),
        )
