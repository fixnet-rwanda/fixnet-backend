import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsSupportAgent, IsFinanceAdmin, IsSystemAdmin
from apps.users.models import User
from apps.technicians.models import TechnicianProfile, TechnicianContent
from apps.jobs.models import JobBooking
from apps.payments.models import PaymentTransaction
from .serializers import (
    VerifyTechnicianSerializer,
    ContentModerationSerializer,
    DisputeRefundSerializer,
    PricingConfigSerializer,
    SuspendUserSerializer,
)


class VerifyTechnicianView(APIView):
    permission_classes = [IsAuthenticated, IsSupportAgent]

    def patch(self, request, id):
        tech = get_object_or_404(TechnicianProfile, id=id)
        serializer = VerifyTechnicianSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tech.verification_status = data["verification_status"]
        tech.rejection_reason = data.get("rejection_reason")
        tech.save(update_fields=["verification_status", "rejection_reason"])

        # Check if trial can activate (TECH-05)
        tech.check_and_activate_trial()

        return Response(
            {
                "verification_status": tech.verification_status,
                "rejection_reason": tech.rejection_reason,
                "is_searchable": tech.is_searchable,
            },
            status=status.HTTP_200_OK,
        )


class ModerateContentView(APIView):
    permission_classes = [IsAuthenticated, IsSupportAgent]

    def delete(self, request, id):
        content = get_object_or_404(TechnicianContent, id=id)
        serializer = ContentModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content.moderation_status = "rejected"
        content.save(update_fields=["moderation_status"])

        return Response(
            {"status": "content_moderated", "reason": serializer.validated_data["reason"]},
            status=status.HTTP_200_OK,
        )


class DisputeRefundView(APIView):
    permission_classes = [IsAuthenticated, (IsSupportAgent | IsFinanceAdmin | IsSystemAdmin)]

    def post(self, request, id):
        booking = get_object_or_404(JobBooking, id=id)
        serializer = DisputeRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        booking.status = "disputed"
        booking.save(update_fields=["status"])

        return Response(
            {
                "status": "refund_processed",
                "refund_amount_rwf": data["refund_amount_rwf"],
                "internal_notes": data["internal_notes"],
            },
            status=status.HTTP_200_OK,
        )


class PricingConfigView(APIView):
    permission_classes = [IsAuthenticated, IsSystemAdmin]

    def post(self, request):
        serializer = PricingConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )


class RevenueReportCSVView(APIView):
    permission_classes = [IsAuthenticated, (IsFinanceAdmin | IsSystemAdmin)]

    def get(self, request):
        month = request.query_params.get("month", "2026-08")

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="fixnet_revenue_{month}.csv"'

        writer = csv.writer(response)
        writer.writerow(["transaction_ref", "payer_id", "amount_rwf", "method", "status", "date"])

        transactions = PaymentTransaction.objects.filter(status="successful")
        for tx in transactions:
            writer.writerow([
                tx.transaction_ref,
                str(tx.payer_id),
                tx.amount_rwf,
                tx.payment_method,
                tx.status,
                tx.created_at.strftime("%Y-%m-%d"),
            ])

        return response


class SuspendUserView(APIView):
    permission_classes = [IsAuthenticated, IsSystemAdmin]

    def post(self, request, id):
        user = get_object_or_404(User, id=id)
        serializer = SuspendUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.is_active = False
        user.save(update_fields=["is_active"])

        if hasattr(user, "technician_profile"):
            user.technician_profile.is_searchable = False
            user.technician_profile.subscription_status = "suspended"
            user.technician_profile.save(update_fields=["is_searchable", "subscription_status"])

        return Response(
            {"status": "user_suspended", "user_id": str(user.id), "reason": serializer.validated_data["reason"]},
            status=status.HTTP_200_OK,
        )
