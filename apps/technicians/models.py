import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class ServiceCategory(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Service categories"

    def __str__(self):
        return self.name


class TechnicianProfile(models.Model):
    BUSINESS_TYPE_CHOICES = (
        ("individual", "Individual"),
        ("company", "Company"),
    )

    VERIFICATION_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    )

    SUBSCRIPTION_STATUS_CHOICES = (
        ("trial_active", "Trial Active"),
        ("active", "Active"),
        ("lapsed", "Lapsed"),
        ("suspended", "Suspended"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="technician_profile")
    business_name = models.CharField(max_length=150, blank=True)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES, default="individual")
    categories = models.ManyToManyField(ServiceCategory, related_name="technicians")
    id_document_url = models.URLField(max_length=500, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)

    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default="pending")
    training_completed = models.BooleanField(default=False)
    is_searchable = models.BooleanField(default=False)

    subscription_status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, default="lapsed")
    trial_ends_at = models.DateTimeField(null=True, blank=True)

    # Location & Metrics
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, default=-1.9441)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, default=30.0619)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    completed_jobs = models.PositiveIntegerField(default=0)
    is_top_rated = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def check_and_activate_trial(self):
        """
        TECH-05: Automatic free trial activation upon verification + training.
        """
        if self.verification_status == "verified" and self.training_completed:
            if not self.trial_ends_at:
                self.trial_ends_at = timezone.now() + timezone.timedelta(days=30)
            self.subscription_status = "trial_active"
            self.is_searchable = True
            self.save(update_fields=["trial_ends_at", "subscription_status", "is_searchable"])

    def update_reputation_and_badge(self):
        """
        REVIEW-04: Auto-award Top Rated badge if rating >= 4.5 and completed_jobs >= 10.
        """
        if self.rating >= 4.5 and self.completed_jobs >= 10:
            self.is_top_rated = True
        else:
            self.is_top_rated = False
        self.save(update_fields=["is_top_rated"])

    def __str__(self):
        return f"{self.business_name or self.user.phone_number} ({self.verification_status})"


class TechnicianContent(models.Model):
    CONTENT_TYPE_CHOICES = (
        ("photo", "Photo"),
        ("video", "Video"),
    )

    MODERATION_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    technician = models.ForeignKey(TechnicianProfile, on_delete=models.CASCADE, related_name="contents")
    type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default="photo")
    media_url = models.URLField(max_length=500)
    description = models.TextField(blank=True)
    moderation_status = models.CharField(max_length=20, choices=MODERATION_STATUS_CHOICES, default="approved")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.technician.business_name} - {self.type} ({self.created_at})"
