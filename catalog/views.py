from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView

from businesses.selectors import MultipleBusinessesUnsupported, resolve_active_business
from catalog.forms import ProductForm
from catalog.models import Product


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


class ProductCreateView(ProductMutationBusinessMixin, View):
    def get(self, request, *args, **kwargs):
        self.resolve_business(request)
        if self.business_policy_blocked:
            return self.render_business_blocked(request)

        form = ProductForm() if self.active_business is not None else None
        return render(
            request,
            self.template_name,
            self.base_context(
                request,
                form=form,
                page_title="Add product",
                submit_label="Create product",
            ),
        )

    def post(self, request, *args, **kwargs):
        self.resolve_business(request)
        if self.business_policy_blocked or self.active_business is None:
            return self.render_business_blocked(request)

        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.business = self.active_business
            product.save()
            messages.success(request, "Product created.")
            return redirect(get_safe_product_return_url(request))

        return render(
            request,
            self.template_name,
            self.base_context(
                request,
                form=form,
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
        return render(
            request,
            self.template_name,
            self.base_context(
                request,
                form=ProductForm(instance=product),
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
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated.")
            return redirect(get_safe_product_return_url(request))

        return render(
            request,
            self.template_name,
            self.base_context(
                request,
                form=form,
                page_title=f"Edit {product.name}",
                product=product,
                submit_label="Save changes",
            ),
        )
