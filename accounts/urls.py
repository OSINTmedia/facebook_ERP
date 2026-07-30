from django.urls import path

from accounts.views import SellerLoginView, SellerLogoutView

app_name = "accounts"

urlpatterns = [
    path("login/", SellerLoginView.as_view(), name="login"),
    path("logout/", SellerLogoutView.as_view(), name="logout"),
]
