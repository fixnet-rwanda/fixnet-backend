from rest_framework import serializers
from .models import Conversation, Message, Quote


class InitiateConversationSerializer(serializers.Serializer):
    technician_id = serializers.UUIDField()


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "sender_type", "content", "is_masked", "created_at")
        read_only_fields = ("id", "is_masked", "created_at")


class ConversationListSerializer(serializers.ModelSerializer):
    customer_phone = serializers.CharField(source="customer.phone_number", read_only=True)
    technician_name = serializers.CharField(source="technician.business_name", read_only=True)

    class Meta:
        model = Conversation
        fields = ("id", "customer", "customer_phone", "technician", "technician_name", "status", "contact_unlocked", "created_at")


class CreateQuoteSerializer(serializers.Serializer):
    total_price_rwf = serializers.IntegerField(min_value=100)
    scope_notes = serializers.CharField()


class RespondQuoteSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["accept", "decline"])
