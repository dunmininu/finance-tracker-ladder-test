"""
API views for the accounts app.

Handles user authentication, registration, and profile management.
"""

import uuid

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserLoginResponseSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserSignupResponseSerializer,
    UserSignupSerializer,
)


@extend_schema(
    operation_id="createUser",
    tags=["user"],
    summary="Register user",
    description="This endpoint is used to create a user using a valid email and password. Bonus points: strong validation on the password field and error handling.",
    request=UserSignupSerializer,
    responses={
        201: OpenApiResponse(
            response=UserSignupResponseSerializer, description="successful operation"
        ),
        400: OpenApiResponse(description="Invalid input data"),
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    """Register a new user."""
    serializer = UserSignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        response_serializer = UserSignupResponseSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id="loginUser",
    tags=["user"],
    summary="Logs user into the system",
    description="This endpoint is used to log a user in.",
    request=UserLoginSerializer,
    responses={
        200: OpenApiResponse(
            response=UserLoginResponseSerializer, description="successful operation"
        ),
        400: OpenApiResponse(description="Invalid username/password"),
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """Log in a user and return JWT tokens."""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        response_data = {
            "user": user,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }

        response_serializer = UserLoginResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id="logoutUser",
    tags=["user"],
    summary="Logs out current logged in user",
    description="This endpoint invalidates the refresh token and kills the user session.",
    request=UserLogoutSerializer,
    responses={
        200: OpenApiResponse(description="User logged out successfully"),
        400: OpenApiResponse(description="Invalid refresh token"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """Log out a user by blacklisting their refresh token."""
    serializer = UserLogoutSerializer(data=request.data)
    if serializer.is_valid():
        try:
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)

            # Verify the token belongs to the current user
            if token.payload.get("user_id") != str(request.user.id):
                return Response(
                    {"detail": "Invalid refresh token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Blacklist the token
            token.blacklist()
            return Response(
                {"detail": "User logged out successfully"}, status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id="getUserByID",
    tags=["user"],
    summary="Get user by user ID",
    description="",
    methods=["GET"],
    responses={
        200: OpenApiResponse(
            response=UserProfileSerializer, description="successful operation"
        ),
        400: OpenApiResponse(description="Invalid user ID"),
        404: OpenApiResponse(description="User not found"),
    },
)
@extend_schema(
    operation_id="updateUser",
    tags=["user"],
    summary="Update user",
    description="This can only be done by the logged in user.",
    methods=["PUT"],
    request=UserProfileUpdateSerializer,
    responses={
        200: OpenApiResponse(description="User details updated successfully!"),
        404: OpenApiResponse(description="User not found"),
    },
)
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def user_profile(request, userID):
    """Get or update user profile by ID."""
    try:
        user_uuid = uuid.UUID(userID)
    except ValueError:
        return Response(
            {"detail": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Users can only access their own profile
    if str(request.user.id) != user_uuid:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        serializer = UserProfileUpdateSerializer(
            request.user, data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "User details updated successfully!"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
