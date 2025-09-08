"""
API views for the finance app.

Handles income and expenditure CRUD operations with proper authentication and permissions.
"""

import uuid

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Expenditure, Income
from .serializers import (
    ExpenditureCreateUpdateSerializer,
    ExpenditureDetailSerializer,
    ExpenditureSerializer,
    IncomeCreateUpdateSerializer,
    IncomeDetailSerializer,
    IncomeSerializer,
)

# Income Views


@extend_schema(
    operation_id="getUserIncome",
    tags=["income"],
    summary="Get user's income data",
    description="This endpoint returns the user's income",
    methods=["GET"],
    responses={
        200: OpenApiResponse(
            response=IncomeSerializer(many=True), description="success"
        )
    },
)
@extend_schema(
    operation_id="addUserIncome",
    tags=["income"],
    summary="Add income data",
    description="This endpoint allows you to add an income. Bonus points if you can come up with some cool additions.",
    methods=["POST"],
    request=IncomeCreateUpdateSerializer,
    responses={
        201: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "new income added"}
                },
            },
            description="Successful operation",
        )
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_income(request):
    """Get all income records or add a new income record for the authenticated user."""
    if request.method == "GET":
        incomes = Income.objects.filter(user=request.user)
        serializer = IncomeSerializer(incomes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
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
    summary="Get income data by ID",
    description="",
    methods=["GET"],
    responses={
        200: OpenApiResponse(
            response=IncomeDetailSerializer, description="successful operation"
        ),
        400: OpenApiResponse(description="Invalid income ID"),
        404: OpenApiResponse(description="Income not found"),
    },
)
@extend_schema(
    operation_id="updateIncomeByID",
    tags=["income"],
    summary="Update income data by ID",
    description="",
    methods=["PUT"],
    request=IncomeCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=IncomeCreateUpdateSerializer, description="successful operation"
        ),
        400: OpenApiResponse(description="Invalid income ID"),
        404: OpenApiResponse(description="Income not found"),
    },
)
@extend_schema(
    operation_id="deleteIncomeByID",
    tags=["income"],
    summary="Delete income data by ID",
    description="",
    methods=["DELETE"],
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "income deleted successfully",
                    }
                },
            },
            description="successful operation",
        ),
        400: OpenApiResponse(
            description="Invalid income ID / some other type of error"
        ),
        404: OpenApiResponse(description="Income not found"),
    },
)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def income_detail(request, incomeID):
    """Get, update, or delete a specific income record by ID."""
    try:
        income_uuid = uuid.UUID(incomeID)
    except ValueError:
        return Response(
            {"detail": "Invalid income ID"}, status=status.HTTP_400_BAD_REQUEST
        )

    income = get_object_or_404(Income, id=income_uuid, user=request.user)

    if request.method == "GET":
        serializer = IncomeDetailSerializer(income)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        serializer = IncomeCreateUpdateSerializer(
            income, data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        income.delete()
        return Response(
            {"message": "income deleted successfully"}, status=status.HTTP_200_OK
        )


# Expenditure Views


@extend_schema(
    operation_id="getUserExpenditure",
    tags=["expenditure"],
    summary="Get user's expenditure data",
    description="This endpoint returns the user's expenditure",
    methods=["GET"],
    responses={
        200: OpenApiResponse(
            response=ExpenditureSerializer(many=True), description="success"
        )
    },
)
@extend_schema(
    operation_id="addUserExpenditure",
    tags=["expenditure"],
    summary="Add expenditure data",
    description="This endpoint allows you to add an expenditure",
    methods=["POST"],
    request=ExpenditureCreateUpdateSerializer,
    responses={
        201: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "new expenditure added"}
                },
            },
            description="Successful operation",
        )
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_expenditure(request):
    """Get all expenditure records or add a new expenditure record for the authenticated user."""
    if request.method == "GET":
        expenditures = Expenditure.objects.filter(user=request.user)
        serializer = ExpenditureSerializer(expenditures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
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
    summary="Get expenditure data by ID",
    description="",
    methods=["GET"],
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
@extend_schema(
    operation_id="updateExpenditureByID",
    tags=["expenditure"],
    summary="Update expenditure data by ID",
    description="",
    methods=["PUT"],
    request=ExpenditureCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=ExpenditureDetailSerializer, description="successful operation"
        ),
        400: OpenApiResponse(description="Invalid expenditure ID"),
        404: OpenApiResponse(description="Expenditure not found"),
    },
)
@extend_schema(
    operation_id="deleteExpenditureByID",
    tags=["expenditure"],
    summary="Delete expenditure data by ID",
    description="",
    methods=["DELETE"],
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "expenditure deleted successfully",
                    }
                },
            },
            description="successful operation",
        ),
        400: OpenApiResponse(description="Invalid expenditure ID"),
        404: OpenApiResponse(description="Expenditure not found"),
    },
)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def expenditure_detail(request, expenditureID):
    """Get, update, or delete a specific expenditure record by ID."""
    try:
        expenditure_uuid = uuid.UUID(expenditureID)
    except ValueError:
        return Response(
            {"detail": "Invalid expenditure ID"}, status=status.HTTP_400_BAD_REQUEST
        )

    expenditure = get_object_or_404(Expenditure, id=expenditure_uuid, user=request.user)

    if request.method == "GET":
        serializer = ExpenditureDetailSerializer(expenditure)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        serializer = ExpenditureCreateUpdateSerializer(
            expenditure, data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            # Return the updated expenditure in detail format
            detail_serializer = ExpenditureDetailSerializer(expenditure)
            return Response(detail_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        expenditure.delete()
        return Response(
            {"message": "expenditure deleted successfully"}, status=status.HTTP_200_OK
        )
