from django.urls import path

from catalog.views import (
    ChoiceVocabularyView,
    ProductAddSimilarView,
    ProductArchiveView,
    ProductCreateView,
    ProductListView,
    ProductMediaView,
    ProductRestoreView,
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
    path(
        "products/<int:pk>/add-similar/",
        ProductAddSimilarView.as_view(),
        name="product_add_similar",
    ),
    path(
        "products/<int:pk>/archive/",
        ProductArchiveView.as_view(),
        name="product_archive",
    ),
    path(
        "products/<int:pk>/restore/",
        ProductRestoreView.as_view(),
        name="product_restore",
    ),
    path("products/<int:pk>/edit/", ProductUpdateView.as_view(), name="product_edit"),
]
