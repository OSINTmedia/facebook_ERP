from django.urls import path

from catalog.views import (
    ChoiceVocabularyView,
    ProductCreateView,
    ProductListView,
    ProductMediaView,
    ProductUpdateView,
    ReadyReplyView,
)

app_name = "catalog"

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product_list"),
    path("products/add/", ProductCreateView.as_view(), name="product_create"),
    path(
        "products/media/<int:pk>/",
        ProductMediaView.as_view(),
        name="product_media",
    ),
    path(
        "products/vocabulary/",
        ChoiceVocabularyView.as_view(),
        name="choice_vocabulary",
    ),
    path(
        "products/<int:pk>/ready-reply/",
        ReadyReplyView.as_view(),
        name="product_ready_reply",
    ),
    path("products/<int:pk>/edit/", ProductUpdateView.as_view(), name="product_edit"),
]
