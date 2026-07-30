"""Project-level views for the minimal application shell."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class ShellHomeView(LoginRequiredMixin, TemplateView):
    """Minimal authenticated shell until seller feature pages are introduced."""

    template_name = "shell/home.html"
    extra_context = {"current_nav": "dashboard"}
