from django.urls import path

from catalog.views import ProductListView

app_name = "catalog"

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product_list"),
]
