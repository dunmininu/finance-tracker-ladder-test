"""
Custom User model for the Personal Expense Tracker API.

Uses UUID primary keys and email-based authentication.
"""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with UUID primary key and email authentication.

    Inherits from AbstractUser to maintain Django's built-in user functionality
    while customizing the primary key and authentication method.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the user",
    )

    email = models.EmailField(
        unique=True, help_text="Email address used for authentication"
    )

    # Override username to make it optional since we use email for auth
    username = models.CharField(
        max_length=150, unique=True, help_text="Username for display purposes"
    )

    # Tell Django to use email as the username field for authentication
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    first_name = models.CharField(
        max_length=150, blank=True, help_text="User's first name"
    )

    last_name = models.CharField(
        max_length=150, blank=True, help_text="User's last name"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the user account was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True, help_text="When the user account was last updated"
    )

    class Meta:
        db_table = "accounts_user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} ({self.username})"

    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the user's short name."""
        return self.first_name or self.username
