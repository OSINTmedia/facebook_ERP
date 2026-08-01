from django.contrib import admin

from catalog.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "lifecycle", "created_at", "updated_at")
    list_filter = ("lifecycle", "created_at", "updated_at")
    search_fields = ("name", "description", "business__name", "business__owner__email")
    autocomplete_fields = ("business",)
    ordering = ("name", "id")
