from django.urls import path
from .views import (
    PayBookingDepositView,
    PaymentWebhookView,
    PaymentReceiptView,
)

urlpatterns = [
    path("booking-deposit", PayBookingDepositView.as_view(), name="payment-booking-deposit"),
    path("webhook", PaymentWebhookView.as_view(), name="payment-webhook"),
    path("<str:id>/receipt", PaymentReceiptView.as_view(), name="payment-receipt"),
]
