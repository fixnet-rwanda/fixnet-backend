from rest_framework import serializers
from .models import TechnicianProfile, TechnicianContent, ServiceCategory


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ("id", "name", "description")


class TechnicianRegisterSerializer(serializers.Serializer):
    business_type = serializers.ChoiceField(choices=TechnicianProfile.BUSINESS_TYPE_CHOICES)
    business_name = serializers.CharField(max_length=150, required=False, default="")
    service_categories = serializers.ListField(child=serializers.CharField(), allow_empty=False)
    id_document_url = serializers.URLField(required=True)


class TechnicianContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicianContent
        fields = ("id", "type", "media_url", "description", "moderation_status", "created_at")
        read_only_fields = ("id", "moderation_status", "created_at")


class TechnicianSearchResultSerializer(serializers.ModelSerializer):
    service_categories = serializers.SerializerMethodField()
    distance_km = serializers.FloatField(default=2.3)

    class Meta:
        model = TechnicianProfile
        fields = (
            "id",
            "business_name",
            "service_categories",
            "rating",
            "completed_jobs",
            "is_top_rated",
            "distance_km",
        )

    def get_service_categories(self, obj):
        return [c.id for c in obj.categories.all()]


class TechnicianDetailSerializer(serializers.ModelSerializer):
    service_categories = ServiceCategorySerializer(source="categories", many=True, read_only=True)
    contents = TechnicianContentSerializer(many=True, read_only=True)

    class Meta:
        model = TechnicianProfile
        fields = (
            "id",
            "business_name",
            "business_type",
            "service_categories",
            "rating",
            "completed_jobs",
            "is_top_rated",
            "contents",
            "verification_status",
            "created_at",
        )


class OnboardingCompleteSerializer(serializers.Serializer):
    training_completed = serializers.BooleanField()
