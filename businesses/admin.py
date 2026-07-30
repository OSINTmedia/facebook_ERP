from django.contrib import admin

from businesses.models import Business


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "owner__email")
    autocomplete_fields = ("owner",)
    ordering = ("name", "id")
