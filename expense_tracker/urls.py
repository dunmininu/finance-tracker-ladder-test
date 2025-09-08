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

from accounts import views as accounts_views
from finance import views as finance_views

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
    path("auth/signup", accounts_views.signup, name="signup"),
    path("auth/login", accounts_views.login, name="login"),
    path("auth/logout", accounts_views.logout, name="logout"),
    path(
        "auth/user/<str:userID>/profile",
        accounts_views.user_profile,
        name="user_profile",
    ),
    # User finance endpoints (exact paths from OpenAPI spec)
    path("user/income", finance_views.user_income, name="user_income"),
    path(
        "user/income/<str:incomeID>", finance_views.income_detail, name="income_detail"
    ),
    path("user/expenditure", finance_views.user_expenditure, name="user_expenditure"),
    path(
        "user/expenditure/<str:expenditureID>",
        finance_views.expenditure_detail,
        name="expenditure_detail",
    ),
]
