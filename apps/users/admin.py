from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "phone_number", "email", "role", "preferred_language", "is_active", "created_at")
    list_filter = ("role", "preferred_language", "is_active")
    search_fields = ("phone_number", "email", "id")
    ordering = ("-created_at",)
