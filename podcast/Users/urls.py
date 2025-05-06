from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, VerifyEmailView,
    PasswordResetRequestView, PasswordResetConfirmView,
    AdminOnlyView, AuthenticatedOnlyView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'), # New email verification endpoint
    path('password/forgot/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('admin-only/', AdminOnlyView.as_view(), name='admin_only'), # Example admin endpoint
    path('authenticated-only/', AuthenticatedOnlyView.as_view(), name='authenticated_only'), # Example authenticated endpoint
]
