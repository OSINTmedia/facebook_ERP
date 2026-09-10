"""Root URL configuration for the project scaffold."""
from django.contrib import admin
from django.urls import include, path

from dashboard.views import DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="shell_home"),
    path("accounts/", include("accounts.urls")),
    path("inventory/", include("inventory.urls")),
    path("", include("catalog.urls")),
    path("admin/", admin.site.urls),
]
