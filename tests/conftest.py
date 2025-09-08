"""
Pytest configuration and fixtures for the Personal Expense Tracker API.
"""

import pytest
from model_bakery import baker
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    return APIClient()


@pytest.fixture
def user():
    """Create a test user."""
    return baker.make(User, email="test@example.com", username="testuser")


@pytest.fixture
def other_user():
    """Create another test user."""
    return baker.make(User, email="other@example.com", username="otheruser")


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def income_data():
    """Sample income data for testing."""
    return {"nameOfRevenue": "Salary", "amount": 5000.00}


@pytest.fixture
def expenditure_data():
    """Sample expenditure data for testing."""
    return {"category": "transport", "nameOfItem": "Bus fare", "estimatedAmount": 50.00}
