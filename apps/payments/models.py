import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.conversations.models import Quote
from apps.technicians.models import TechnicianProfile


class PaymentTransaction(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("successful", "Successful"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    )

    METHOD_CHOICES = (
        ("momo", "Mobile Money"),
        ("card", "Card"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_ref = models.CharField(max_length=64, unique=True, db_index=True)
    quote = models.ForeignKey(Quote, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    amount_rwf = models.PositiveIntegerField()  # Smallest currency unit (PAY-01)
    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES, default="momo")
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    gateway_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_ref} - {self.amount_rwf} RWF ({self.status})"


class TechnicianSubscription(models.Model):
    STATUS_CHOICES = (
        ("trial_active", "Trial Active"),
        ("active", "Active"),
        ("lapsed", "Lapsed"),
        ("suspended", "Suspended"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    technician = models.ForeignKey(TechnicianProfile, on_delete=models.CASCADE, related_name="subscriptions")
    plan_id = models.CharField(max_length=50, default="plan_monthly_pro")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="trial_active")
    amount_rwf = models.PositiveIntegerField(default=15000)
    start_date = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.technician.business_name} - {self.plan_id} ({self.status})"
