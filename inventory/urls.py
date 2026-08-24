from django.urls import path

from inventory.views import ChoiceStockMutationView

app_name = "inventory"

urlpatterns = [
    path(
        "choices/<int:choice_pk>/adjust/",
        ChoiceStockMutationView.as_view(),
        name="choice_stock_adjust",
    ),
]
