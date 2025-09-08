"""
URL configuration for expense_tracker project.

Routes URLs to views matching the OpenAPI specification exactly.
"""

from django.contrib import admin
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from accounts.views import UserViewSet
from finance.views import ExpenditureViewSet, IncomeViewSet

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Authentication endpoints (exact paths from OpenAPI spec)
    path("auth/signup", UserViewSet.as_view({"post": "signup"}), name="signup"),
    path("auth/login", UserViewSet.as_view({"post": "login"}), name="login"),
    path("auth/logout", UserViewSet.as_view({"post": "logout"}), name="logout"),
    path(
        "auth/user/<str:pk>/profile",
        UserViewSet.as_view({"get": "retrieve", "put": "update"}),
        name="user_profile",
    ),
    # User finance endpoints (exact paths from OpenAPI spec)
    path(
        "user/income",
        IncomeViewSet.as_view({"get": "list", "post": "create"}),
        name="user_income",
    ),
    path(
        "user/income/<str:pk>",
        IncomeViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="income_detail",
    ),
    path(
        "user/expenditure",
        ExpenditureViewSet.as_view({"get": "list", "post": "create"}),
        name="user_expenditure",
    ),
    path(
        "user/expenditure/<str:pk>",
        ExpenditureViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="expenditure_detail",
    ),
]
