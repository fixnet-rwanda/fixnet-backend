import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.technicians.models import TechnicianProfile
from core.utils import mask_contact_info


class Conversation(models.Model):
    STATUS_CHOICES = (
        ("chat_opened", "Chat Opened"),
        ("active", "Active"),
        ("closed", "Closed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_conversations")
    technician = models.ForeignKey(TechnicianProfile, on_delete=models.CASCADE, related_name="technician_conversations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="chat_opened")
    contact_unlocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conv {self.id} (Cust: {self.customer.phone_number} - Tech: {self.technician.business_name})"


class Message(models.Model):
    SENDER_TYPE_CHOICES = (
        ("customer", "Customer"),
        ("technician", "Technician"),
        ("system", "System"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    sender_type = models.CharField(max_length=15, choices=SENDER_TYPE_CHOICES)
    content = models.TextField()
    original_content = models.TextField(blank=True)
    is_masked = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.conversation.contact_unlocked and self.sender_type != "system":
            self.original_content = self.content
            masked_text, masked = mask_contact_info(self.content)
            self.content = masked_text
            self.is_masked = masked
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Msg {self.id} by {self.sender_type}"


class Quote(models.Model):
    STATUS_CHOICES = (
        ("sent", "Sent"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
        ("expired", "Expired"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="quotes")
    technician = models.ForeignKey(TechnicianProfile, on_delete=models.CASCADE, related_name="quotes")
    total_price_rwf = models.PositiveIntegerField()  # Stored as integer currency (PAY-01)
    scope_notes = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="sent")
    required_booking_deposit_rwf = models.PositiveIntegerField(default=2500)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # CHAT-04: Quotes expire in 48 hours
            self.expires_at = timezone.now() + timezone.timedelta(hours=48)
        if not self.required_booking_deposit_rwf:
            # 10% of total quote or default flat deposit
            self.required_booking_deposit_rwf = max(2000, int(self.total_price_rwf * 0.1))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Quote {self.id} ({self.total_price_rwf} RWF - {self.status})"
