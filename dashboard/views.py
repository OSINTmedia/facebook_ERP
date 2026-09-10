"""Authenticated action-first seller Dashboard."""

from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView

from businesses.selectors import MultipleBusinessesUnsupported, resolve_active_business
from dashboard.attention import ATTENTION_FILTER_GROUPS, build_seller_attention


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "shell/home.html"

    def get(self, request, *args, **kwargs):
        self.business_policy_blocked = False
        self.active_business = None

        try:
            self.active_business = resolve_active_business(request.user)
        except MultipleBusinessesUnsupported:
            self.business_policy_blocked = True
            return self.render_to_response(self.get_context_data(), status=409)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attention = None
        if self.active_business is not None:
            attention = build_seller_attention(business=self.active_business)

        context.update(
            {
                "active_business": self.active_business,
                "attention": attention,
                "business_policy_blocked": self.business_policy_blocked,
                "current_nav": "dashboard",
                "dashboard_return_url": reverse("shell_home"),
                "missing_information_workspace_url": self._workspace_url(
                    "missing_information"
                ),
                "low_stock_workspace_url": self._workspace_url("low_stock"),
                "sold_out_workspace_url": self._workspace_url("sold_out"),
                "partial_stock_workspace_url": self._workspace_url(
                    "partial_stock"
                ),
            }
        )
        return context

    @staticmethod
    def _workspace_url(attention_filter):
        if attention_filter not in ATTENTION_FILTER_GROUPS:
            raise ValueError("Unsupported Dashboard drilldown.")
        query = urlencode(
            (("attention", attention_filter), ("origin", "dashboard"))
        )
        return f'{reverse("catalog:product_list")}?{query}'
