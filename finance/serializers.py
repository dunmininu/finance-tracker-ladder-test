"""
Serializers for the finance app.

Handles income and expenditure data with camelCase field mapping for API responses.
"""


from decimal import Decimal

from rest_framework import serializers

from .models import Expenditure, Income


class IncomeSerializer(serializers.ModelSerializer):
    """
    Serializer for Income model with camelCase field mapping.

    Maps snake_case database fields to camelCase API response fields.
    """

    nameOfRevenue = serializers.CharField(source="name_of_revenue")
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )

    class Meta:
        model = Income
        fields = ["id", "nameOfRevenue", "amount"]
        read_only_fields = ["id"]

    def validate_amount(self, value):
        """Ensure amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value


class IncomeDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Income view with camelCase field mapping.

    Used for GET /user/income/{incomeID} endpoint.
    """

    nameOfRevenue = serializers.CharField(source="name_of_revenue")
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )

    class Meta:
        model = Income
        fields = ["id", "nameOfRevenue", "amount"]
        read_only_fields = ["id"]


class IncomeCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Income records.

    Used for POST and PUT operations on income endpoints.
    """

    nameOfRevenue = serializers.CharField(source="name_of_revenue")
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )

    class Meta:
        model = Income
        fields = ["nameOfRevenue", "amount"]

    def validate_amount(self, value):
        """Ensure amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def create(self, validated_data):
        """Create income record for the authenticated user."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ExpenditureSerializer(serializers.ModelSerializer):
    """
    Serializer for Expenditure model with camelCase field mapping.

    Maps snake_case database fields to camelCase API response fields.
    """

    nameOfItem = serializers.CharField(source="name_of_item")
    estimatedAmount = serializers.DecimalField(
        source="estimated_amount",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    class Meta:
        model = Expenditure
        fields = ["id", "category", "nameOfItem", "estimatedAmount"]
        read_only_fields = ["id"]

    def validate_estimatedAmount(self, value):
        """Ensure estimated amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Estimated amount must be positive.")
        return value


class ExpenditureDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Expenditure view with camelCase field mapping.

    Used for GET /user/expenditure/{expenditureID} endpoint.
    """

    nameOfItem = serializers.CharField(source="name_of_item")
    estimatedAmount = serializers.DecimalField(
        source="estimated_amount",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    class Meta:
        model = Expenditure
        fields = ["id", "category", "nameOfItem", "estimatedAmount"]
        read_only_fields = ["id"]


class ExpenditureCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Expenditure records.

    Used for POST and PUT operations on expenditure endpoints.
    """

    nameOfItem = serializers.CharField(source="name_of_item")
    estimatedAmount = serializers.DecimalField(
        source="estimated_amount",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    class Meta:
        model = Expenditure
        fields = ["category", "nameOfItem", "estimatedAmount"]

    def validate_estimatedAmount(self, value):
        """Ensure estimated amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Estimated amount must be positive.")
        return value

    def create(self, validated_data):
        """Create expenditure record for the authenticated user."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
