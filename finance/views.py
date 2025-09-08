"""
API views for the finance app.

Handles income and expenditure management using ViewSets.
"""

import uuid

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Expenditure, Income
from .serializers import (
    ExpenditureCreateUpdateSerializer,
    ExpenditureDetailSerializer,
    ExpenditureSerializer,
    IncomeCreateUpdateSerializer,
    IncomeDetailSerializer,
    IncomeSerializer,
)


class IncomeViewSet(
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
):
    """
    ViewSet for income operations.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return incomes for the authenticated user."""
        return Income.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ["list"]:
            return IncomeSerializer
        elif self.action in ["retrieve"]:
            return IncomeDetailSerializer
        elif self.action in ["create", "update"]:
            return IncomeCreateUpdateSerializer
        return IncomeSerializer

    @extend_schema(
        operation_id="getUserIncome",
        tags=["income"],
        summary="Get user income",
        description="This endpoint is used to get all income records for the authenticated user.",
        responses={
            200: OpenApiResponse(
                response=IncomeSerializer(many=True), description="success"
            )
        },
    )
    def list(self, request, *args, **kwargs):
        """Get all income records for the authenticated user."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        operation_id="addIncome",
        tags=["income"],
        summary="Add new income",
        description="This endpoint is used to add a new income record for the authenticated user.",
        request=IncomeCreateUpdateSerializer,
        responses={
            201: OpenApiResponse(
                description="Successful operation",
                examples={
                    "application/json": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "example": "new income added"}
                        },
                    }
                },
            )
        },
    )
    def create(self, request, *args, **kwargs):
        """Create a new income record for the authenticated user."""
        serializer = IncomeCreateUpdateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "new income added"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="getIncomeByID",
        tags=["income"],
        summary="Get income by ID",
        description="This endpoint is used to get a specific income record by ID.",
        responses={
            200: OpenApiResponse(
                response=IncomeDetailSerializer, description="successful operation"
            ),
            400: OpenApiResponse(description="Invalid income ID"),
            404: OpenApiResponse(description="Income not found"),
        },
    )
    def retrieve(self, request, pk=None, *args, **kwargs):
        """Get a specific income record by ID."""
        try:
            income_uuid = uuid.UUID(pk)
        except ValueError:
            return Response(
                {"detail": "Invalid income ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        income = get_object_or_404(Income, id=income_uuid, user=request.user)
        serializer = IncomeDetailSerializer(income)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="updateIncome",
        tags=["income"],
        summary="Update income",
        description="This endpoint is used to update an existing income record.",
        request=IncomeCreateUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=IncomeCreateUpdateSerializer,
                description="successful operation",
            ),
            400: OpenApiResponse(description="Invalid income ID"),
            404: OpenApiResponse(description="Income not found"),
        },
    )
    def update(self, request, pk=None, *args, **kwargs):
        """Update an existing income record."""
        try:
            income_uuid = uuid.UUID(pk)
        except ValueError:
            return Response(
                {"detail": "Invalid income ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        income = get_object_or_404(Income, id=income_uuid, user=request.user)
        serializer = IncomeCreateUpdateSerializer(
            income, data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="deleteIncome",
        tags=["income"],
        summary="Delete income",
        description="This endpoint is used to delete an income record.",
        responses={
            200: OpenApiResponse(
                description="successful operation",
                examples={
                    "application/json": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "example": "income deleted successfully",
                            }
                        },
                    }
                },
            ),
            400: OpenApiResponse(
                description="Invalid income ID / some other type of error"
            ),
            404: OpenApiResponse(description="Income not found"),
        },
    )
    def destroy(self, request, pk=None, *args, **kwargs):
        """Delete an income record."""
        try:
            income_uuid = uuid.UUID(pk)
        except ValueError:
            return Response(
                {"detail": "Invalid income ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        income = get_object_or_404(Income, id=income_uuid, user=request.user)
        income.delete()
        return Response(
            {"message": "income deleted successfully"}, status=status.HTTP_200_OK
        )


class ExpenditureViewSet(
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
):
    """
    ViewSet for expenditure operations.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return expenditures for the authenticated user."""
        return Expenditure.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ["list"]:
            return ExpenditureSerializer
        elif self.action in ["retrieve"]:
            return ExpenditureDetailSerializer
        elif self.action in ["create", "update"]:
            return ExpenditureCreateUpdateSerializer
        return ExpenditureSerializer

    @extend_schema(
        operation_id="getUserExpenditure",
        tags=["expenditure"],
        summary="Get user expenditure",
        description="This endpoint is used to get all expenditure records for the authenticated user.",
        responses={
            200: OpenApiResponse(
                response=ExpenditureSerializer(many=True), description="success"
            )
        },
    )
    def list(self, request, *args, **kwargs):
        """Get all expenditure records for the authenticated user."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        operation_id="addExpenditure",
        tags=["expenditure"],
        summary="Add new expenditure",
        description="This endpoint is used to add a new expenditure record for the authenticated user.",
        request=ExpenditureCreateUpdateSerializer,
        responses={
            201: OpenApiResponse(
                description="Successful operation",
                examples={
                    "application/json": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "example": "new expenditure added",
                            }
                        },
                    }
                },
            )
        },
    )
    def create(self, request, *args, **kwargs):
        """Create a new expenditure record for the authenticated user."""
        serializer = ExpenditureCreateUpdateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "new expenditure added"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="getExpenditureByID",
        tags=["expenditure"],
        summary="Get expenditure by ID",
        description="This endpoint is used to get a specific expenditure record by ID.",
        responses={
            200: OpenApiResponse(
                response=ExpenditureDetailSerializer, description="successful operation"
            ),
            400: OpenApiResponse(description="Invalid expenditure ID"),
            404: OpenApiResponse(
                description="Expenditure not foun"
            ),  # Preserving typo from spec
        },
    )
    def retrieve(self, request, pk=None, *args, **kwargs):
        """Get a specific expenditure record by ID."""
        try:
            expenditure_uuid = uuid.UUID(pk)
        except ValueError:
            return Response(
                {"detail": "Invalid expenditure ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        expenditure = get_object_or_404(
            Expenditure, id=expenditure_uuid, user=request.user
        )
        serializer = ExpenditureDetailSerializer(expenditure)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="updateExpenditure",
        tags=["expenditure"],
        summary="Update expenditure",
        description="This endpoint is used to update an existing expenditure record.",
        request=ExpenditureCreateUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=ExpenditureDetailSerializer, description="successful operation"
            ),
            400: OpenApiResponse(description="Invalid expenditure ID"),
            404: OpenApiResponse(description="Expenditure not found"),
        },
    )
    def update(self, request, pk=None, *args, **kwargs):
        """Update an existing expenditure record."""
        try:
            expenditure_uuid = uuid.UUID(pk)
        except ValueError:
            return Response(
                {"detail": "Invalid expenditure ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        expenditure = get_object_or_404(
            Expenditure, id=expenditure_uuid, user=request.user
        )
        serializer = ExpenditureCreateUpdateSerializer(
            expenditure, data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            # Return the updated expenditure in detail format
            detail_serializer = ExpenditureDetailSerializer(expenditure)
            return Response(detail_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="deleteExpenditure",
        tags=["expenditure"],
        summary="Delete expenditure",
        description="This endpoint is used to delete an expenditure record.",
        responses={
            200: OpenApiResponse(
                description="successful operation",
                examples={
                    "application/json": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "example": "expenditure deleted successfully",
                            }
                        },
                    }
                },
            ),
            400: OpenApiResponse(description="Invalid expenditure ID"),
            404: OpenApiResponse(description="Expenditure not found"),
        },
    )
    def destroy(self, request, pk=None, *args, **kwargs):
        """Delete an expenditure record."""
        try:
            expenditure_uuid = uuid.UUID(pk)
        except ValueError:
            return Response(
                {"detail": "Invalid expenditure ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        expenditure = get_object_or_404(
            Expenditure, id=expenditure_uuid, user=request.user
        )
        expenditure.delete()
        return Response(
            {"message": "expenditure deleted successfully"}, status=status.HTTP_200_OK
        )
