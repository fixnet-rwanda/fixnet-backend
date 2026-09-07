from rest_framework import serializers


class VerifyTechnicianSerializer(serializers.Serializer):
    verification_status = serializers.ChoiceField(choices=["verified", "rejected"])
    rejection_reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class ContentModerationSerializer(serializers.Serializer):
    reason = serializers.CharField()


class DisputeRefundSerializer(serializers.Serializer):
    refund_amount_rwf = serializers.IntegerField(min_value=1)
    internal_notes = serializers.CharField()


class PricingConfigSerializer(serializers.Serializer):
    booking_deposit_type = serializers.ChoiceField(choices=["flat", "percentage"], default="flat")
    default_deposit_amount_rwf = serializers.IntegerField(min_value=500)
    default_trial_days = serializers.IntegerField(min_value=7, max_value=90)


class SuspendUserSerializer(serializers.Serializer):
    reason = serializers.CharField()
