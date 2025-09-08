"""
Finance models for Income and Expenditure tracking.

Both models use UUID primary keys and are linked to the custom User model.
"""

import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Income(models.Model):
    """
    Model representing a user's income record.

    Stores income information including source name and amount.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the income record",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="incomes",
        help_text="User who owns this income record",
    )

    name_of_revenue = models.CharField(
        max_length=120, help_text="Name or description of the revenue source"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Income amount (must be positive)",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the income record was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True, help_text="When the income record was last updated"
    )

    class Meta:
        db_table = "finance_income"
        verbose_name = "Income"
        verbose_name_plural = "Incomes"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.name_of_revenue}: ${self.amount} ({self.user.email})"


class Expenditure(models.Model):
    """
    Model representing a user's expenditure record.

    Stores expenditure information including category, item name, and estimated amount.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the expenditure record",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenditures",
        help_text="User who owns this expenditure record",
    )

    category = models.CharField(
        max_length=60,
        help_text="Category of the expenditure (e.g., transport, food, entertainment)",
    )

    name_of_item = models.CharField(
        max_length=120, help_text="Name or description of the item/service"
    )

    estimated_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Estimated expenditure amount (must be positive)",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the expenditure record was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True, help_text="When the expenditure record was last updated"
    )

    class Meta:
        db_table = "finance_expenditure"
        verbose_name = "Expenditure"
        verbose_name_plural = "Expenditures"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["category"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.category}: {self.name_of_item} - ${self.estimated_amount} ({self.user.email})"
