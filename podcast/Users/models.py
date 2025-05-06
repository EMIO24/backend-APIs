# In your Django app's models.py
import uuid # For generating unique email verification tokens
from django.db import models
from django.contrib.auth.models import AbstractUser # Import AbstractUser
from django.conf import settings
from django.utils import timezone

# Extend the built-in User model to add email_verified_at
class CustomUser(AbstractUser):
    # Django's AbstractUser already includes:
    # username, first_name, last_name, email, is_staff, is_active,
    # date_joined, last_login, groups, user_permissions, password

    email_verified_at = models.DateTimeField(null=True, blank=True) # Add this field

    # You can add other custom fields here if needed later,
    # but for Task 1, this is the main addition.

    # Ensure you set AUTH_USER_MODEL = 'your_app_name.CustomUser' in settings.py

    def __str__(self):
        return self.email or self.username # Represent user by email if available

class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True) # Use a sufficiently long unique token
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """Checks if the token is still valid (e.g., not expired)."""
        # Configure token expiry time in settings.py (e.g., 1 hour)
        expiry_time = timezone.now() - timezone.timedelta(hours=settings.PASSWORD_RESET_TIMEOUT_HOURS)
        return self.created_at > expiry_time

    def __str__(self):
        return f"Password Reset Token for {self.user.email}"

# We'll also need a model for email verification tokens
class EmailVerificationToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # One token per user
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # Using UUID for unique tokens
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
         """Checks if the token is still valid (e.g., not expired)."""
         # Configure token expiry time in settings.py (e.g., 24 hours)
         expiry_time = timezone.now() - timezone.timedelta(hours=settings.EMAIL_VERIFICATION_TIMEOUT_HOURS)
         return self.created_at > expiry_time


    def __str__(self):
        return f"Email Verification Token for {self.user.email}"

