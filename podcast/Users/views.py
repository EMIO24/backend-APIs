# In your Django app's views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token # For Token Authentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny # Permissions
from django.contrib.auth import authenticate, login, logout # Django auth functions
from django.conf import settings
from django.core.mail import send_mail # For sending emails
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.urls import reverse # To generate URLs for email links

from .serializers import (
    RegisterSerializer, LoginSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    UserSerializer # Keep UserSerializer for response
)
from .models import CustomUser, PasswordResetToken, EmailVerificationToken # Use CustomUser
import uuid # Needed for UUID token generation


# Helper function to send email verification email
def send_verification_email(user):
    # Delete any existing verification tokens for this user
    EmailVerificationToken.objects.filter(user=user).delete()

    # Create a new verification token
    verification_token = EmailVerificationToken.objects.create(user=user)

    # --- Send Email ---
    # You'll need to build the verification link pointing to your frontend or API endpoint
    # Option 1: Link directly to an API endpoint that handles verification
    # verification_link = f"{settings.BASE_API_URL}{reverse('verify_email')}?token={verification_token.token}" # Configure BASE_API_URL in settings

    # Option 2: Link to a frontend page that calls your API endpoint
    verification_link = f"{settings.FRONTEND_VERIFY_EMAIL_URL}?token={verification_token.token}&email={user.email}" # Configure frontend URL in settings

    subject = 'Verify Your Email Address'
    # Create an HTML email template (e.g., emails/verify_email.html)
    html_message = render_to_string('emails/verify_email.html', {'verification_link': verification_link, 'user': user})
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
    # -----------


# --- Registration ---
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all() # Use CustomUser
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny] # Anyone can register

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save() # User is created with is_active=False

        # Mandatory: Send email verification immediately after registration
        send_verification_email(user)

        headers = self.get_success_headers(serializer.data)
        # Return a message indicating that verification is required
        return Response(
            {"detail": "User registered successfully. Please check your email to verify your account."},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

# --- Email Verification ---
class VerifyEmailView(APIView):
    permission_classes = [AllowAny] # This endpoint is accessed publicly via email link

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        email = request.data.get('email')

        if not token or not email:
            return Response({'detail': 'Token and email are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email) # Use CustomUser
        except CustomUser.DoesNotExist: # Use CustomUser
             # Be vague for security
            return Response({'detail': 'Invalid or expired verification link.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification_token = EmailVerificationToken.objects.get(user=user, token=token)
        except EmailVerificationToken.DoesNotExist:
             # Be vague for security
            return Response({'detail': 'Invalid or expired verification link.'}, status=status.HTTP_400_BAD_REQUEST)

        if not verification_token.is_valid():
             # Be vague for security
             return Response({'detail': 'Invalid or expired verification link.'}, status=status.HTTP_400_BAD_REQUEST)


        # Mandatory: Mark user as active and set verification timestamp
        user.is_active = True
        user.email_verified_at = timezone.now()
        user.save()

        # Delete the used verification token
        verification_token.delete()

        return Response({'detail': 'Email verified successfully. You can now log in.'}, status=status.HTTP_200_OK)


# --- Login (using Token Authentication) ---
class LoginView(APIView):
    permission_classes = [AllowAny] # Allow anyone to attempt login

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) # Validation includes active status check

        user = serializer.validated_data['user']

        # Use DRF's Token authentication
        token, created = Token.objects.get_or_create(user=user)

        # Return UserSerializer data along with the token
        user_serializer = UserSerializer(user) # Use UserSerializer
        return Response({'token': token.key, 'user': user_serializer.data}, status=status.HTTP_200_OK)


# --- Logout (for Token Authentication) ---
class LogoutView(APIView):
    permission_classes = [IsAuthenticated] # Mandatory: Only logged-in users can log out

    def post(self, request, *args, **kwargs):
        try:
            # Delete the user's token to log them out
            request.user.auth_token.delete()
        except Exception:
             # Handle cases where token might be missing for some reason
             pass # Or log the error
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)


# --- Password Reset Request ---
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny] # Anyone can request a password reset

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = CustomUser.objects.get(email=email) # Use CustomUser
        except CustomUser.DoesNotExist: # Use CustomUser
            # Mandatory: Return success even if user not found to prevent enumeration
            return Response({'detail': 'If a user with that email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)

        # Delete any existing tokens for this user to prevent multiple valid tokens
        PasswordResetToken.objects.filter(user=user).delete()

        # Generate a new token
        token = uuid.uuid4() # Using UUID for password reset tokens too

        # Create the password reset token record
        PasswordResetToken.objects.create(user=user, token=token)

        # --- Send Email ---
        # You would typically render an HTML template for the email
        # Configure FRONTEND_RESET_PASSWORD_URL in settings
        reset_link = f"{settings.FRONTEND_RESET_PASSWORD_URL}?token={token}&email={email}"
        subject = 'Password Reset Request'
        html_message = render_to_string('emails/password_reset.html', {'reset_link': reset_link, 'user': user}) # Create this template
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email

        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
        # -----------

        # Mandatory: Return a success response (again, generic)
        return Response({'detail': 'If a user with that email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)


# --- Password Reset Confirmation ---
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny] # This endpoint is accessed publicly via email link

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user'] # Get user from validated data
        new_password = serializer.validated_data['password']
        reset_token_obj = serializer.validated_data['reset_token_obj'] # Get token object from validated data

        # Mandatory: Set the new password (handles hashing)
        user.set_password(new_password)
        user.save()

        # Mandatory: Delete the used token after successful reset
        reset_token_obj.delete()

        return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)


# --- Admin Flag Check Example (using a placeholder endpoint) ---
class AdminOnlyView(APIView):
    # Mandatory: Requires user to be logged in AND is_staff or is_superuser
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Welcome, Admin! You have access to this restricted area."}, status=status.HTTP_200_OK)

# --- Example of a view requiring authentication ---
class AuthenticatedOnlyView(APIView):
     # Mandatory: Requires user to be logged in and active (due to LoginSerializer check)
     permission_classes = [IsAuthenticated]

     def get(self, request, *args, **kwargs):
         # request.user will be the authenticated CustomUser object
         return Response(
             {"message": f"Hello, {request.user.username}! You are authenticated and your email verification status is: {request.user.email_verified_at is not None}"},
             status=status.HTTP_200_OK
        )

# Create your views here.
