"""
Tests for authentication endpoints.

Covers signup, login, logout, and profile management.
"""

import pytest
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User


@pytest.mark.django_db
class TestUserSignup:
    """Test user registration functionality."""

    def test_signup_success(self, api_client):
        """Test successful user registration."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "john@example.com",
            "password": "SecurePass123!",
        }

        response = api_client.post("/auth/signup", data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert "email" in response.data
        assert response.data["email"] == "john@example.com"
        assert response.data["message"] == "User created successfully"

        # Verify user was created
        user = User.objects.get(email="john@example.com")
        assert user.username == "johndoe"
        assert user.first_name == "John"
        assert user.last_name == "Doe"

    def test_signup_weak_password_fails(self, api_client):
        """Test that weak passwords are rejected."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "john@example.com",
            "password": "123",  # Too short
        }

        response = api_client.post("/auth/signup", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    def test_signup_duplicate_email_fails(self, api_client, user):
        """Test that duplicate emails are rejected."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": user.email,  # Duplicate email
            "password": "SecurePass123!",
        }

        response = api_client.post("/auth/signup", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_signup_duplicate_username_fails(self, api_client, user):
        """Test that duplicate usernames are rejected."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": user.username,  # Duplicate username
            "email": "john@example.com",
            "password": "SecurePass123!",
        }

        response = api_client.post("/auth/signup", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data


@pytest.mark.django_db
class TestUserLogin:
    """Test user login functionality."""

    def test_login_success(self, api_client, user):
        """Test successful user login."""
        # Set a known password for the user
        user.set_password("password")
        user.save()

        data = {"email": user.email, "password": "password"}

        response = api_client.post("/auth/login", data, format="json")

        # Debug: print the response if it fails
        if response.status_code != status.HTTP_200_OK:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")

        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.data
        assert "id" in response.data["data"]
        assert "email" in response.data["data"]
        assert "tokens" in response.data["data"]
        assert "access_token" in response.data["data"]["tokens"]
        assert "refresh_token" in response.data["data"]["tokens"]
        assert response.data["data"]["email"] == user.email

    def test_login_bad_credentials_400(self, api_client, user):
        """Test login with invalid credentials."""
        # Set a known password for the user
        user.set_password("password")
        user.save()

        data = {"email": user.email, "password": "wrongpassword"}

        response = api_client.post("/auth/login", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data

    def test_login_nonexistent_user_400(self, api_client):
        """Test login with non-existent user."""
        data = {"email": "nonexistent@example.com", "password": "password"}

        response = api_client.post("/auth/login", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogout:
    """Test user logout functionality."""

    def test_logout_success(self, authenticated_client, user):
        """Test successful user logout."""
        # Get refresh token
        refresh = RefreshToken.for_user(user)
        refresh_token = str(refresh)

        data = {"refresh": refresh_token}

        response = authenticated_client.post("/auth/logout", data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "User logged out successfully"

    def test_logout_invalid_refresh_400(self, authenticated_client):
        """Test logout with invalid refresh token."""
        data = {"refresh": "invalid_token"}

        response = authenticated_client.post("/auth/logout", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid refresh token"

    def test_logout_wrong_user_refresh_400(self, authenticated_client, other_user):
        """Test logout with refresh token from different user."""
        refresh = RefreshToken.for_user(other_user)
        refresh_token = str(refresh)

        data = {"refresh": refresh_token}

        response = authenticated_client.post("/auth/logout", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid refresh token"


@pytest.mark.django_db
class TestUserProfile:
    """Test user profile management."""

    def test_get_own_profile_200(self, authenticated_client, user):
        """Test getting own profile."""
        response = authenticated_client.get(f"/auth/user/{user.id}/profile")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(user.id)
        assert response.data["email"] == user.email
        assert response.data["username"] == user.username
        assert response.data["first_name"] == user.first_name
        assert response.data["last_name"] == user.last_name

    def test_get_other_profile_404(self, authenticated_client, user, other_user):
        """Test getting another user's profile returns 404."""
        response = authenticated_client.get(f"/auth/user/{other_user.id}/profile")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "User not found"

    def test_get_invalid_user_id_404(self, authenticated_client, user):
        """Test getting profile with invalid UUID."""
        response = authenticated_client.get("/auth/user/invalid-uuid/profile")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_own_profile_200(self, authenticated_client, user):
        """Test updating own profile."""
        data = {"first_name": "Updated", "last_name": "Name", "username": "updateduser"}

        response = authenticated_client.put(
            f"/auth/user/{user.id}/profile", data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "User details updated successfully!"

        # Verify user was updated
        user.refresh_from_db()
        assert user.first_name == "Updated"
        assert user.last_name == "Name"
        assert user.username == "updateduser"

    def test_update_other_profile_404(self, authenticated_client, user, other_user):
        """Test updating another user's profile returns 404."""
        data = {"first_name": "Hacked", "last_name": "Name"}

        response = authenticated_client.put(
            f"/auth/user/{other_user.id}/profile", data, format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "User not found"

    def test_update_profile_duplicate_username_400(
        self, authenticated_client, user, other_user
    ):
        """Test updating profile with duplicate username."""
        data = {"username": other_user.username}  # Duplicate username

        response = authenticated_client.put(
            f"/auth/user/{user.id}/profile", data, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data


@pytest.mark.django_db
class TestAuthenticationRequired:
    """Test that authentication is required for protected endpoints."""

    def test_profile_endpoints_require_auth(self, api_client, user):
        """Test that profile endpoints require authentication."""
        # Test GET profile without auth
        response = api_client.get(f"/auth/user/{user.id}/profile")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Test PUT profile without auth
        response = api_client.put(f"/auth/user/{user.id}/profile", {}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_requires_auth(self, api_client):
        """Test that logout requires authentication."""
        data = {"refresh": "some_token"}

        response = api_client.post("/auth/logout", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
