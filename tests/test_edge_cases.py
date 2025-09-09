"""
Additional edge case tests for the expense tracker API.

Tests various edge cases and validation scenarios.
"""


import pytest
from rest_framework import status


@pytest.mark.django_db
class TestEdgeCases:
    """Test various edge cases and validation scenarios."""

    def test_income_amount_edge_cases(self, authenticated_client, user):
        """Test income amount validation edge cases."""
        # Test very large amount
        data = {
            "nameOfRevenue": "Large Income",
            "amount": "100000000001",  # Over 100 billion
        }
        response = authenticated_client.post("/user/income", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "no more than 10 digits before the decimal point" in str(response.data)

        # Test amount with too many decimal places
        data = {
            "nameOfRevenue": "Precise Income",
            "amount": "100.123",  # 3 decimal places
        }
        response = authenticated_client.post("/user/income", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "more than 2 decimal places" in str(response.data)

        # Test zero amount
        data = {"nameOfRevenue": "Zero Income", "amount": "0"}
        response = authenticated_client.post("/user/income", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "greater than or equal to 0.01" in str(response.data)

    def test_income_name_edge_cases(self, authenticated_client, user):
        """Test income name validation edge cases."""
        # Test empty name
        data = {"nameOfRevenue": "", "amount": "100"}
        response = authenticated_client.post("/user/income", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "may not be blank" in str(response.data)

        # Test whitespace-only name
        data = {"nameOfRevenue": "   ", "amount": "100"}
        response = authenticated_client.post("/user/income", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "may not be blank" in str(response.data)

        # Test very long name
        data = {
            "nameOfRevenue": "A" * 121,  # 121 characters (over 120 limit)
            "amount": "100",
        }
        response = authenticated_client.post("/user/income", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "exceed 120 characters" in str(response.data)

    def test_expenditure_edge_cases(self, authenticated_client, user):
        """Test expenditure validation edge cases."""
        # Test empty category
        data = {"category": "", "nameOfItem": "Test Item", "estimatedAmount": "100"}
        response = authenticated_client.post("/user/expenditure", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "may not be blank" in str(response.data)

        # Test very long category
        data = {
            "category": "A" * 61,  # 61 characters (over 60 limit)
            "nameOfItem": "Test Item",
            "estimatedAmount": "100",
        }
        response = authenticated_client.post("/user/expenditure", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "no more than 60 characters" in str(response.data)

    def test_user_registration_edge_cases(self, api_client):
        """Test user registration validation edge cases."""
        # Test invalid email format
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "invalid-email",
            "password": "SecurePass123!",
        }
        response = api_client.post("/auth/signup", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Test very long email
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "a" * 250 + "@example.com",  # Over 254 chars
            "password": "SecurePass123!",
        }
        response = api_client.post("/auth/signup", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "no more than 254 characters" in str(response.data)

        # Test short username
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "ab",  # Only 2 characters
            "email": "john@example.com",
            "password": "SecurePass123!",
        }
        response = api_client.post("/auth/signup", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "at least 3 characters" in str(response.data)

        # Test username with invalid characters
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "john@doe",  # Contains @
            "email": "john@example.com",
            "password": "SecurePass123!",
        }
        response = api_client.post("/auth/signup", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "letters, numbers, underscores" in str(response.data)

    def test_concurrent_operations(self, authenticated_client, user):
        """Test concurrent operations edge cases."""
        # Create an income record
        data = {"nameOfRevenue": "Salary", "amount": "5000"}
        response = authenticated_client.post("/user/income", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        # The response should contain a message, not an id
        assert "message" in response.data

        # Get the income list to find the created income
        response = authenticated_client.get("/user/income")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        income_id = response.data[0]["id"]

        # Try to update the same record with different data
        update_data = {"nameOfRevenue": "Updated Salary", "amount": "6000"}
        response = authenticated_client.put(
            f"/user/income/{income_id}", update_data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["nameOfRevenue"] == "Updated Salary"

    def test_unicode_handling(self, authenticated_client, user):
        """Test Unicode character handling."""
        # Test Unicode in income name
        data = {"nameOfRevenue": "Salary 💰 with emoji", "amount": "5000"}
        response = authenticated_client.post("/user/income", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.data

        # Verify the Unicode was saved correctly by getting the list
        response = authenticated_client.get("/user/income")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["nameOfRevenue"] == "Salary 💰 with emoji"

        # Test Unicode in expenditure
        data = {
            "category": "Food 🍕",
            "nameOfItem": "Pizza with ñoño",
            "estimatedAmount": "25.50",
        }
        response = authenticated_client.post("/user/expenditure", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.data

        # Verify the Unicode was saved correctly
        response = authenticated_client.get("/user/expenditure")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["category"] == "Food 🍕"
        assert response.data[0]["nameOfItem"] == "Pizza with ñoño"
