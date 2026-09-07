from rest_framework import serializers
from .models import PaymentTransaction, TechnicianSubscription


class BookingDepositSerializer(serializers.Serializer):
    quote_id = serializers.UUIDField()
    payment_method = serializers.ChoiceField(choices=["momo", "card"], default="momo")
    phone_number = serializers.CharField(max_length=20)


class WebhookSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()
    quote_id = serializers.UUIDField(required=False)
    status = serializers.ChoiceField(choices=["successful", "failed"])
    amount_rwf = serializers.IntegerField()


class SubscriptionPaymentSerializer(serializers.Serializer):
    plan_id = serializers.CharField(default="plan_monthly_pro")
    payment_method = serializers.ChoiceField(choices=["momo", "card"], default="momo")
    phone_number = serializers.CharField(max_length=20)
