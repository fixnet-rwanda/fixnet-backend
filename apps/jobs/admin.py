from django.contrib import admin
from .models import JobBooking, JobReview


@admin.register(JobBooking)
class JobBookingAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "technician", "service_category", "deposit_amount_rwf", "status", "created_at")
    list_filter = ("status", "service_category")


@admin.register(JobReview)
class JobReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "technician", "customer", "rating", "created_at")
    list_filter = ("rating",)
