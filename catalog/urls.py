from django.urls import path

from catalog.views import ProductCreateView, ProductListView, ProductUpdateView

app_name = "catalog"

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product_list"),
    path("products/add/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/edit/", ProductUpdateView.as_view(), name="product_edit"),
]
