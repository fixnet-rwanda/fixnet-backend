from django.contrib import admin
from .models import Conversation, Message, Quote


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "technician", "status", "contact_unlocked", "created_at")
    list_filter = ("status", "contact_unlocked")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender_type", "is_masked", "created_at")
    list_filter = ("sender_type", "is_masked")


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("id", "technician", "total_price_rwf", "required_booking_deposit_rwf", "status", "created_at", "expires_at")
    list_filter = ("status",)
