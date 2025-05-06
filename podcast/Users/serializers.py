# In your Django app's serializers.py

from rest_framework import serializers
from django.contrib.auth import authenticate # Django's built-in authenticate function
from django.conf import settings
from django.utils import timezone
from rest_framework.authtoken.models import Token
from .models import CustomUser, PasswordResetToken, EmailVerificationToken # Use CustomUser


class UserSerializer(serializers.ModelSerializer):
    email_verified = serializers.SerializerMethodField() # Add a method field

    class Meta:
        model = CustomUser # Use CustomUser
        fields = ('id', 'username', 'email', 'is_staff', 'email_verified') # Include email_verified

    def get_email_verified(self, obj):
        return obj.email_verified_at is not None # Check if the timestamp is set


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser # Use CustomUser
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        # Create user as inactive until email is verified
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False # User is inactive until email verification
        )
        # Email verification token will be generated and sent in the view
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False) # Allow login with username or email
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not (username or email):
            raise serializers.ValidationError("Must include either username or email.")

        user = None
        if username:
            user = authenticate(username=username, password=password)
        elif email:
            try:
                temp_user = CustomUser.objects.get(email=email) # Use CustomUser
                user = authenticate(username=temp_user.username, password=password)
            except CustomUser.DoesNotExist: # Use CustomUser
                pass

        if user is None:
            raise serializers.ValidationError("Invalid credentials.")

        # Mandatory: Check if user is active (email verified)
        if not user.is_active:
             raise serializers.ValidationError("Please verify your email address before logging in.")

        # Attach the authenticated user to the validated data
        data['user'] = user
        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Optionally, check if a user with this email exists
        # Although the view handles the "silent" success message,
        # you might want to validate existence here if you need the user object later in the serializer.
        # For this flow, validating existence in the view is fine to prevent enumeration.
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        token = data.get('token')
        password = data.get('password')
        password_confirm = data.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError("Passwords do not match.")

        # Check if a valid token exists for this email and get the user via the token
        try:
            reset_token = PasswordResetToken.objects.select_related('user').get(email=email, token=token) # Use select_related for user
            if not reset_token.is_valid(): # Use the model method to check expiry
                 raise serializers.ValidationError("Invalid or expired token.")
            data['user'] = reset_token.user # Attach the user object
            data['reset_token_obj'] = reset_token # Attach the token object for deletion
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired token.")

        return data