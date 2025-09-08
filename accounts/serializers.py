"""
Serializers for the accounts app.

Handles user registration, authentication, and profile management.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSignupSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates password strength and creates new user accounts.
    """

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text="Password must meet Django's password validation requirements",
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password"]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "username": {"required": True},
            "email": {"required": True},
        }

    def validate_email(self, value):
        """Ensure email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """Ensure username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def create(self, validated_data):
        """Create a new user with hashed password."""
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSignupResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for user signup response.

    Returns user ID, email, and success message as per OpenAPI spec.
    """

    message = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "message"]

    def get_message(self, obj):
        """Return success message."""
        return "User created successfully"


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Accepts email and password for authentication.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Validate user credentials."""
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError(
                    "Invalid email/password combination.", code="invalid_credentials"
                )
            if not user.is_active:
                raise serializers.ValidationError(
                    "User account is disabled.", code="account_disabled"
                )
            attrs["user"] = user
        else:
            raise serializers.ValidationError(
                "Must include email and password.", code="missing_credentials"
            )

        return attrs


class UserLoginResponseSerializer(serializers.Serializer):
    """
    Serializer for user login response.

    Returns nested data structure with user info and tokens as per OpenAPI spec.
    """

    data = serializers.SerializerMethodField()

    def get_data(self, obj):
        """Return nested data structure."""
        return {
            "id": str(obj["user"].id),
            "email": obj["user"].email,
            "tokens": {
                "access_token": obj["access_token"],
                "refresh_token": obj["refresh_token"],
            },
        }


class UserLogoutSerializer(serializers.Serializer):
    """
    Serializer for user logout.

    Accepts refresh token for blacklisting.
    """

    refresh = serializers.CharField(required=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.

    Returns user profile information as per OpenAPI spec.
    """

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email"]
        read_only_fields = ["id", "email"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.

    Allows updating first_name, last_name, and username only.
    """

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]

    def validate_username(self, value):
        """Ensure username is unique (excluding current user)."""
        user = self.context["request"].user
        if User.objects.filter(username=value).exclude(id=user.id).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value
