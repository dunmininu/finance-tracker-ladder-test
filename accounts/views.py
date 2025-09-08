"""
API views for the accounts app.

Handles user authentication, registration, and profile management using ViewSets.
"""

import uuid

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    UserLoginResponseSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserSignupResponseSerializer,
    UserSignupSerializer,
)


class UserViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    """
    ViewSet for user operations including signup, login, logout, and profile management.
    """

    queryset = User.objects.all()
    # Remove default permission_classes - we'll handle this in get_permissions()

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "signup":
            return UserSignupSerializer
        elif self.action == "login":
            return UserLoginSerializer
        elif self.action == "logout":
            return UserLogoutSerializer
        elif self.action == "retrieve":
            return UserProfileSerializer
        elif self.action == "update":
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action in ["signup", "login"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @extend_schema(
        operation_id="createUser",
        tags=["user"],
        summary="Register user",
        description="This endpoint is used to register a new user.",
        request=UserSignupSerializer,
        responses={
            201: OpenApiResponse(
                response=UserSignupResponseSerializer,
                description="successful operation",
            ),
            400: OpenApiResponse(description="Invalid input"),
        },
        auth=[],  # Explicitly disable authentication for this endpoint
    )
    @action(detail=False, methods=["post"])
    def signup(self, request):
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
        auth=[],  # Explicitly disable authentication for this endpoint
    )
    @action(detail=False, methods=["post"])
    def login(self, request):
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
    @action(detail=False, methods=["post"])
    def logout(self, request):
        """Log out a user by blacklisting their refresh token."""
        serializer = UserLogoutSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data["refresh"]
                token = RefreshToken(refresh_token)

                # Verify the token belongs to the authenticated user
                if token.payload.get("user_id") != str(request.user.id):
                    return Response(
                        {"detail": "Invalid refresh token"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                token.blacklist()
                return Response(
                    {"detail": "User logged out successfully"},
                    status=status.HTTP_200_OK,
                )
            except TokenError:
                return Response(
                    {"detail": "Invalid refresh token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="getUserByID",
        tags=["user"],
        summary="Get user by user ID",
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
    def retrieve(self, request, pk=None):
        """Get user profile by ID."""
        try:
            uuid.UUID(pk)
        except ValueError:
            return Response(
                {"detail": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Users can only access their own profile
        if str(request.user.id) != pk:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """Update user profile by ID."""
        try:
            uuid.UUID(pk)
        except ValueError:
            return Response(
                {"detail": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Users can only update their own profile
        if str(request.user.id) != pk:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

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
