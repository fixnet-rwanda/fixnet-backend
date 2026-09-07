import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.conversations.models import Quote
from apps.technicians.models import TechnicianProfile


class JobBooking(models.Model):
    STATUS_CHOICES = (
        ("quote_accepted", "Quote Accepted"),
        ("deposit_paid", "Deposit Paid"),
        ("completed", "Completed"),
        ("disputed", "Disputed"),
        ("cancelled", "Cancelled"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote = models.OneToOneField(Quote, on_delete=models.CASCADE, related_name="job_booking")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_jobs")
    technician = models.ForeignKey(TechnicianProfile, on_delete=models.CASCADE, related_name="technician_jobs")
    service_category = models.CharField(max_length=100, default="General")
    deposit_amount_rwf = models.PositiveIntegerField(default=2500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="quote_accepted")
    unlocked_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Job {self.id} ({self.service_category} - {self.status})"


class JobReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(JobBooking, on_delete=models.CASCADE, related_name="review")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    technician = models.ForeignKey(TechnicianProfile, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()  # 1 to 5
    comment = models.TextField(blank=True)
    photo_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate technician rating (REVIEW-03) and auto-award badge (REVIEW-04)
        tech_reviews = JobReview.objects.filter(technician=self.technician)
        total_count = tech_reviews.count()
        if total_count > 0:
            avg_rating = sum([r.rating for r in tech_reviews]) / total_count
            self.technician.rating = round(avg_rating, 2)
            self.technician.completed_jobs = JobBooking.objects.filter(technician=self.technician, status="completed").count()
            self.technician.update_reputation_and_badge()

    def __str__(self):
        return f"Review for {self.technician.business_name}: {self.rating} stars"
