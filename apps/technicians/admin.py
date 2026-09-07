from django.contrib import admin
from .models import ServiceCategory, TechnicianProfile, TechnicianContent


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(TechnicianProfile)
class TechnicianProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "business_name", "business_type", "verification_status", "is_searchable", "subscription_status", "rating")
    list_filter = ("verification_status", "is_searchable", "subscription_status", "business_type")
    search_fields = ("business_name", "user__phone_number")


@admin.register(TechnicianContent)
class TechnicianContentAdmin(admin.ModelAdmin):
    list_display = ("id", "technician", "type", "moderation_status", "created_at")
    list_filter = ("moderation_status", "type")
