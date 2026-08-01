from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from businesses.selectors import MultipleBusinessesUnsupported, resolve_active_business
from catalog.models import Product


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
