"""Root URL configuration for the project scaffold."""
from django.contrib import admin
from django.urls import path

from config.views import ShellHomeView

urlpatterns = [
    path("", ShellHomeView.as_view(), name="shell_home"),
    path("admin/", admin.site.urls),
]
