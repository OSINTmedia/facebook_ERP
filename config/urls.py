"""Root URL configuration for the project scaffold."""
from django.contrib import admin
from django.urls import include, path

from config.views import ShellHomeView

urlpatterns = [
    path("", ShellHomeView.as_view(), name="shell_home"),
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
]
