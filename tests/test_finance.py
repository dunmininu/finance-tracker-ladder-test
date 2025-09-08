"""
Tests for finance endpoints.

Covers income and expenditure CRUD operations.
"""

import pytest
from model_bakery import baker
from rest_framework import status

from finance.models import Expenditure, Income


@pytest.mark.django_db
class TestIncomeEndpoints:
    """Test income CRUD operations."""

    def test_list_income_empty_then_create_and_list(
        self, authenticated_client, user, income_data
    ):
        """Test listing income when empty, then creating and listing again."""
        # Initially empty
        response = authenticated_client.get("/user/income")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

        # Create income
        response = authenticated_client.post("/user/income", income_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["message"] == "new income added"

        # List income again
        response = authenticated_client.get("/user/income")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["nameOfRevenue"] == income_data["nameOfRevenue"]
        assert float(response.data[0]["amount"]) == income_data["amount"]

    def test_create_income_201_shape_ok(self, authenticated_client, income_data):
        """Test creating income returns correct response shape."""
        response = authenticated_client.post("/user/income", income_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["message"] == "new income added"

        # Verify income was created
        income = Income.objects.get(name_of_revenue=income_data["nameOfRevenue"])
        assert income.amount == income_data["amount"]

    def test_create_income_invalid_data_400(self, authenticated_client):
        """Test creating income with invalid data."""
        data = {"nameOfRevenue": "", "amount": -100}  # Empty name  # Negative amount

        response = authenticated_client.post("/user/income", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "nameOfRevenue" in response.data or "amount" in response.data

    def test_get_income_by_id_200(self, authenticated_client, user):
        """Test getting income by ID."""
        income = baker.make(Income, user=user, name_of_revenue="Salary", amount=5000)

        response = authenticated_client.get(f"/user/income/{income.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(income.id)
        assert response.data["nameOfRevenue"] == "Salary"
        assert float(response.data["amount"]) == 5000.0

    def test_get_income_invalid_id_400(self, authenticated_client):
        """Test getting income with invalid UUID."""
        response = authenticated_client.get("/user/income/invalid-uuid")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid income ID"

    def test_get_income_not_found_404(self, authenticated_client, other_user):
        """Test getting income that doesn't exist or belongs to another user."""
        income = baker.make(Income, user=other_user)

        response = authenticated_client.get(f"/user/income/{income.id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_income_200_returns_request_body_shape(
        self, authenticated_client, user
    ):
        """Test updating income returns correct response shape."""
        income = baker.make(
            Income, user=user, name_of_revenue="Old Salary", amount=4000
        )

        data = {"nameOfRevenue": "New Salary", "amount": 6000}

        response = authenticated_client.put(
            f"/user/income/{income.id}", data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["nameOfRevenue"] == "New Salary"
        assert float(response.data["amount"]) == 6000.0

        # Verify income was updated
        income.refresh_from_db()
        assert income.name_of_revenue == "New Salary"
        assert income.amount == 6000

    def test_update_income_not_found_404(self, authenticated_client, other_user):
        """Test updating income that doesn't exist or belongs to another user."""
        income = baker.make(Income, user=other_user)

        data = {"nameOfRevenue": "Hacked Salary", "amount": 999999}

        response = authenticated_client.put(
            f"/user/income/{income.id}", data, format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_income_200_message_ok(self, authenticated_client, user):
        """Test deleting income returns correct message."""
        income = baker.make(Income, user=user)

        response = authenticated_client.delete(f"/user/income/{income.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "income deleted successfully"

        # Verify income was deleted
        assert not Income.objects.filter(id=income.id).exists()

    def test_delete_income_not_found_404(self, authenticated_client, other_user):
        """Test deleting income that doesn't exist or belongs to another user."""
        income = baker.make(Income, user=other_user)

        response = authenticated_client.delete(f"/user/income/{income.id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify income still exists
        assert Income.objects.filter(id=income.id).exists()

    def test_income_ownership_isolation(self, authenticated_client, user, other_user):
        """Test that users can only see their own income records."""
        # Create income for both users
        baker.make(Income, user=user, name_of_revenue="User Salary")
        other_income = baker.make(
            Income, user=other_user, name_of_revenue="Other Salary"
        )

        # List income for authenticated user
        response = authenticated_client.get("/user/income")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["nameOfRevenue"] == "User Salary"

        # Verify user cannot access other user's income
        response = authenticated_client.get(f"/user/income/{other_income.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestExpenditureEndpoints:
    """Test expenditure CRUD operations."""

    def test_list_expenditure_empty_then_create_and_list(
        self, authenticated_client, expenditure_data
    ):
        """Test listing expenditure when empty, then creating and listing again."""
        # Initially empty
        response = authenticated_client.get("/user/expenditure")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

        # Create expenditure
        response = authenticated_client.post(
            "/user/expenditure", expenditure_data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["message"] == "new expenditure added"

        # List expenditure again
        response = authenticated_client.get("/user/expenditure")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["category"] == expenditure_data["category"]
        assert response.data[0]["nameOfItem"] == expenditure_data["nameOfItem"]
        assert (
            float(response.data[0]["estimatedAmount"])
            == expenditure_data["estimatedAmount"]
        )

    def test_create_expenditure_201_shape_ok(
        self, authenticated_client, expenditure_data
    ):
        """Test creating expenditure returns correct response shape."""
        response = authenticated_client.post(
            "/user/expenditure", expenditure_data, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["message"] == "new expenditure added"

        # Verify expenditure was created
        expenditure = Expenditure.objects.get(
            name_of_item=expenditure_data["nameOfItem"]
        )
        assert expenditure.estimated_amount == expenditure_data["estimatedAmount"]

    def test_create_expenditure_invalid_data_400(self, authenticated_client):
        """Test creating expenditure with invalid data."""
        data = {
            "category": "",  # Empty category
            "nameOfItem": "",  # Empty name
            "estimatedAmount": -50,  # Negative amount
        }

        response = authenticated_client.post("/user/expenditure", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_expenditure_by_id_200(self, authenticated_client, user):
        """Test getting expenditure by ID."""
        expenditure = baker.make(
            Expenditure,
            user=user,
            category="transport",
            name_of_item="Bus fare",
            estimated_amount=50,
        )

        response = authenticated_client.get(f"/user/expenditure/{expenditure.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(expenditure.id)
        assert response.data["category"] == "transport"
        assert response.data["nameOfItem"] == "Bus fare"
        assert float(response.data["estimatedAmount"]) == 50.0

    def test_get_expenditure_invalid_id_400(self, authenticated_client):
        """Test getting expenditure with invalid UUID."""
        response = authenticated_client.get("/user/expenditure/invalid-uuid")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid expenditure ID"

    def test_get_expenditure_not_found_404(self, authenticated_client, other_user):
        """Test getting expenditure that doesn't exist or belongs to another user."""
        expenditure = baker.make(Expenditure, user=other_user)

        response = authenticated_client.get(f"/user/expenditure/{expenditure.id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_expenditure_200_returns_detail_shape(
        self, authenticated_client, user
    ):
        """Test updating expenditure returns correct response shape."""
        expenditure = baker.make(
            Expenditure,
            user=user,
            category="old_category",
            name_of_item="Old Item",
            estimated_amount=100,
        )

        data = {
            "category": "new_category",
            "nameOfItem": "New Item",
            "estimatedAmount": 200,
        }

        response = authenticated_client.put(
            f"/user/expenditure/{expenditure.id}", data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["category"] == "new_category"
        assert response.data["nameOfItem"] == "New Item"
        assert float(response.data["estimatedAmount"]) == 200.0

        # Verify expenditure was updated
        expenditure.refresh_from_db()
        assert expenditure.category == "new_category"
        assert expenditure.name_of_item == "New Item"
        assert expenditure.estimated_amount == 200

    def test_update_expenditure_not_found_404(self, authenticated_client, other_user):
        """Test updating expenditure that doesn't exist or belongs to another user."""
        expenditure = baker.make(Expenditure, user=other_user)

        data = {
            "category": "hacked_category",
            "nameOfItem": "Hacked Item",
            "estimatedAmount": 999999,
        }

        response = authenticated_client.put(
            f"/user/expenditure/{expenditure.id}", data, format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_expenditure_200_message_ok(self, authenticated_client, user):
        """Test deleting expenditure returns correct message."""
        expenditure = baker.make(Expenditure, user=user)

        response = authenticated_client.delete(f"/user/expenditure/{expenditure.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "expenditure deleted successfully"

        # Verify expenditure was deleted
        assert not Expenditure.objects.filter(id=expenditure.id).exists()

    def test_delete_expenditure_not_found_404(self, authenticated_client, other_user):
        """Test deleting expenditure that doesn't exist or belongs to another user."""
        expenditure = baker.make(Expenditure, user=other_user)

        response = authenticated_client.delete(f"/user/expenditure/{expenditure.id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify expenditure still exists
        assert Expenditure.objects.filter(id=expenditure.id).exists()

    def test_expenditure_ownership_isolation(
        self, authenticated_client, user, other_user
    ):
        """Test that users can only see their own expenditure records."""
        # Create expenditure for both users
        baker.make(Expenditure, user=user, name_of_item="User Item")
        other_expenditure = baker.make(
            Expenditure, user=other_user, name_of_item="Other Item"
        )

        # List expenditure for authenticated user
        response = authenticated_client.get("/user/expenditure")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["nameOfItem"] == "User Item"

        # Verify user cannot access other user's expenditure
        response = authenticated_client.get(f"/user/expenditure/{other_expenditure.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestFinanceAuthenticationRequired:
    """Test that authentication is required for finance endpoints."""

    def test_income_endpoints_require_auth(self, api_client):
        """Test that income endpoints require authentication."""
        # Test GET income without auth
        response = api_client.get("/user/income")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Test POST income without auth
        response = api_client.post("/user/income", {}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Test GET income by ID without auth
        response = api_client.get("/user/income/some-uuid")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_expenditure_endpoints_require_auth(self, api_client):
        """Test that expenditure endpoints require authentication."""
        # Test GET expenditure without auth
        response = api_client.get("/user/expenditure")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Test POST expenditure without auth
        response = api_client.post("/user/expenditure", {}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Test GET expenditure by ID without auth
        response = api_client.get("/user/expenditure/some-uuid")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestSchemaEndpoint:
    """Test API schema generation."""

    def test_schema_endpoint_returns_200_json(self, api_client):
        """Test that schema endpoint returns valid JSON."""
        response = api_client.get("/api/schema/")

        assert response.status_code == status.HTTP_200_OK
        # Just check that it returns some content
        assert len(response.content) > 0
