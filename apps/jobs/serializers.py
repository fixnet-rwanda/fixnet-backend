from rest_framework import serializers
from .models import JobBooking, JobReview


class JobHistorySerializer(serializers.ModelSerializer):
    job_id = serializers.UUIDField(source="id", read_only=True)
    technician_name = serializers.CharField(source="technician.business_name", read_only=True)
    date = serializers.DateTimeField(source="created_at", format="%Y-%m-%d", read_only=True)
    deposit_paid_rwf = serializers.IntegerField(source="deposit_amount_rwf", read_only=True)

    class Meta:
        model = JobBooking
        fields = ("job_id", "technician_name", "service_category", "date", "deposit_paid_rwf", "status")


class ConfirmJobCompletionSerializer(serializers.Serializer):
    completed = serializers.BooleanField()


class SubmitReviewSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, default="")
    photo_url = serializers.URLField(required=False, allow_blank=True, default="")
