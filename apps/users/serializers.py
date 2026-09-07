from rest_framework import serializers
from .models import User


class OTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    channel = serializers.ChoiceField(choices=["sms"], default="sms")


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6, min_length=6)


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class AdminMFAVerifySerializer(serializers.Serializer):
    mfa_token = serializers.CharField()
    totp_code = serializers.CharField(max_length=6, min_length=6)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone_number", "email", "role", "preferred_language", "created_at")
        read_only_fields = ("id", "role", "created_at")


class UpdateLanguageSerializer(serializers.Serializer):
    preferred_language = serializers.ChoiceField(choices=User.LANGUAGE_CHOICES)
