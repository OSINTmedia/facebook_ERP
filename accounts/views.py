from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView

from accounts.forms import SellerAuthenticationForm


class SellerLoginView(LoginView):
    authentication_form = SellerAuthenticationForm
    redirect_authenticated_user = True
    template_name = "accounts/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if (
            settings.DEMO_ACCESS_ENABLED
            and settings.DEMO_USER_EMAIL
            and settings.DEMO_USER_PASSWORD
        ):
            context["demo_access"] = {
                "email": settings.DEMO_USER_EMAIL,
                "password": settings.DEMO_USER_PASSWORD,
            }
        return context


class SellerLogoutView(LogoutView):
    pass
