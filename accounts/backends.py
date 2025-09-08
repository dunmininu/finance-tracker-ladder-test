"""
Custom authentication backend for email-based authentication.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that uses email instead of username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate using email and password."""
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)

        if username is None or password is None:
            return

        try:
            # Try to find user by email
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user
            User().set_password(password)
            return

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

    def get_user(self, user_id):
        """Get user by ID."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
