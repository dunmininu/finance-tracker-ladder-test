"""
URL configuration for accounts app.

Handles authentication and user profile endpoints.
"""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication endpoints
    path("", views.signup, name="signup"),
    path("", views.login, name="login"),
    path("", views.logout, name="logout"),
    # User profile endpoints
    path("", views.get_user_profile, name="get_user_profile"),
    path("", views.update_user_profile, name="update_user_profile"),
]
