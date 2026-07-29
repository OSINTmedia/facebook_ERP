"""Project-level views for the minimal application shell."""
from django.views.generic import TemplateView


class ShellHomeView(TemplateView):
    """Temporary shell route until authenticated seller pages are introduced."""

    template_name = "shell/home.html"
    extra_context = {"current_nav": "dashboard"}
