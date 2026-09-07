from django.contrib import admin
from .models import PaymentTransaction, TechnicianSubscription


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_ref", "payer", "amount_rwf", "payment_method", "status", "created_at")
    list_filter = ("status", "payment_method")
    search_fields = ("transaction_ref", "phone_number")


@admin.register(TechnicianSubscription)
class TechnicianSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("technician", "plan_id", "status", "start_date", "expires_at")
    list_filter = ("status", "plan_id")
