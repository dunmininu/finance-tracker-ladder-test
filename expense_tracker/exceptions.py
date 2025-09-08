"""
Custom exception handlers for the expense tracker API.

Provides consistent error responses and handles edge cases.
"""

import logging
from decimal import InvalidOperation

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import TokenError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.

    Handles various edge cases and provides meaningful error messages.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the error response
        custom_response_data = {
            "error": True,
            "message": "An error occurred",
            "details": response.data,
        }

        # Handle specific exception types
        if isinstance(exc, DjangoValidationError):
            custom_response_data["message"] = "Validation error"
            custom_response_data["details"] = str(exc)
            response.status_code = status.HTTP_400_BAD_REQUEST

        elif isinstance(exc, IntegrityError):
            custom_response_data["message"] = "Data integrity error"
            custom_response_data[
                "details"
            ] = "The operation would violate data constraints"
            response.status_code = status.HTTP_400_BAD_REQUEST

        elif isinstance(exc, TokenError):
            custom_response_data["message"] = "Token error"
            custom_response_data["details"] = "Invalid or expired token"
            response.status_code = status.HTTP_401_UNAUTHORIZED

        elif isinstance(exc, InvalidOperation):
            custom_response_data["message"] = "Invalid operation"
            custom_response_data["details"] = "Invalid decimal operation"
            response.status_code = status.HTTP_400_BAD_REQUEST

        # Log the error for monitoring
        logger.error(f"API Error: {exc}", exc_info=True)

        response.data = custom_response_data

    return response
