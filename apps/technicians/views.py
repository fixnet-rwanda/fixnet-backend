from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from core.permissions import IsTechnician, IsCustomer
from .models import TechnicianProfile, TechnicianContent, ServiceCategory
from .serializers import (
    TechnicianRegisterSerializer,
    TechnicianSearchResultSerializer,
    TechnicianDetailSerializer,
    TechnicianContentSerializer,
    OnboardingCompleteSerializer,
)


class TechnicianRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TechnicianRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Update user role to technician
        request.user.role = "technician"
        request.user.save(update_fields=["role"])

        profile, _ = TechnicianProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "business_type": data["business_type"],
                "business_name": data.get("business_name") or request.user.phone_number or "Technician",
                "id_document_url": data["id_document_url"],
                "verification_status": "pending",
                "subscription_status": "lapsed",
                "is_searchable": False,
            },
        )

        for cat_slug in data["service_categories"]:
            cat, _ = ServiceCategory.objects.get_or_create(id=cat_slug, defaults={"name": cat_slug.capitalize()})
            profile.categories.add(cat)

        return Response(
            {
                "profile_id": str(profile.id),
                "verification_status": profile.verification_status,
                "subscription_status": profile.subscription_status,
                "message": "Registration submitted. Pending admin verification.",
            },
            status=status.HTTP_201_CREATED,
        )


class TechnicianListView(ListAPIView):
    """
    SEARCH-01: Return only technician profiles where is_searchable = TRUE
    AND verification_status = 'verified'.
    """
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = TechnicianSearchResultSerializer

    def get_queryset(self):
        queryset = TechnicianProfile.objects.filter(
            is_searchable=True,
            verification_status="verified",
        )
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(categories__id=category)
        return queryset.distinct()


class TechnicianDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TechnicianDetailSerializer
    queryset = TechnicianProfile.objects.all()
    lookup_field = "id"


class TechnicianContentUploadView(APIView):
    permission_classes = [IsAuthenticated, IsTechnician]

    def post(self, request):
        profile = getattr(request.user, "technician_profile", None)
        if not profile:
            return Response({"error_code": "RESOURCE_NOT_FOUND", "message": "Technician profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TechnicianContentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.save(technician=profile)
        return Response(TechnicianContentSerializer(content).data, status=status.HTTP_201_CREATED)


class TechnicianDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsTechnician]

    def get(self, request):
        profile = getattr(request.user, "technician_profile", None)
        if not profile:
            return Response({"error_code": "RESOURCE_NOT_FOUND", "message": "Technician profile not found."}, status=status.HTTP_404_NOT_FOUND)

        days_remaining = 0
        if profile.trial_ends_at:
            delta = profile.trial_ends_at - timezone.now()
            days_remaining = max(0, delta.days)

        return Response(
            {
                "trial_ends_at": profile.trial_ends_at.isoformat() if profile.trial_ends_at else None,
                "trial_days_remaining": days_remaining,
                "leads_received_this_month": 18,
                "quotes_accepted": profile.completed_jobs,
                "earnings_this_month_rwf": 150000,
            },
            status=status.HTTP_200_OK,
        )


class CompleteTrainingView(APIView):
    permission_classes = [IsAuthenticated, IsTechnician]

    def post(self, request):
        profile = getattr(request.user, "technician_profile", None)
        if not profile:
            return Response({"error_code": "RESOURCE_NOT_FOUND", "message": "Technician profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OnboardingCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile.training_completed = serializer.validated_data["training_completed"]
        profile.save(update_fields=["training_completed"])
        profile.check_and_activate_trial()

        return Response({"training_completed": profile.training_completed, "is_searchable": profile.is_searchable}, status=status.HTTP_200_OK)
