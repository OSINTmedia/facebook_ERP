from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView

from businesses.selectors import MultipleBusinessesUnsupported, resolve_active_business
from catalog.models import Product
from catalog.product_bundles import ProductBundle
from catalog.recognition import recognize_product_preview_for_business


RECOGNITION_PREVIEW_INTENT = "preview_recognition"


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
