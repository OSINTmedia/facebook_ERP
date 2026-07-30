from django.contrib.auth.views import LoginView, LogoutView

from accounts.forms import SellerAuthenticationForm


class SellerLoginView(LoginView):
    authentication_form = SellerAuthenticationForm
    redirect_authenticated_user = True
    template_name = "accounts/login.html"


class SellerLogoutView(LogoutView):
    pass
