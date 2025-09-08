"""
Admin configuration for finance app.
"""

from django.contrib import admin

from .models import Expenditure, Income


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    """Admin configuration for Income model."""

    list_display = ("name_of_revenue", "amount", "user", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("name_of_revenue", "user__email", "user__username")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("user", "name_of_revenue", "amount")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Expenditure)
class ExpenditureAdmin(admin.ModelAdmin):
    """Admin configuration for Expenditure model."""

    list_display = (
        "category",
        "name_of_item",
        "estimated_amount",
        "user",
        "created_at",
    )
    list_filter = ("category", "created_at", "user")
    search_fields = ("category", "name_of_item", "user__email", "user__username")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("user", "category", "name_of_item", "estimated_amount")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
