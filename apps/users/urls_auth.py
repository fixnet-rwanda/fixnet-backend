from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    OTPRequestView,
    OTPVerifyView,
    AdminLoginView,
    AdminMFAVerifyView,
)

urlpatterns = [
    path("otp/request", OTPRequestView.as_view(), name="otp-request"),
    path("otp/verify", OTPVerifyView.as_view(), name="otp-verify"),
    path("token/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("admin/login", AdminLoginView.as_view(), name="admin-login"),
    path("admin/mfa-verify", AdminMFAVerifyView.as_view(), name="admin-mfa-verify"),
]
