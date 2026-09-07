from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from core.permissions import IsCustomer
from apps.conversations.models import Conversation
from .models import JobBooking, JobReview
from .serializers import (
    JobHistorySerializer,
    ConfirmJobCompletionSerializer,
    SubmitReviewSerializer,
)


class JobHistoryView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        jobs = JobBooking.objects.filter(customer=request.user).order_by("-created_at")
        serializer = JobHistorySerializer(jobs, many=True)
        return Response({"jobs": serializer.data}, status=status.HTTP_200_OK)


class OneTapRebookView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request, id):
        past_job = get_object_or_404(JobBooking, id=id, customer=request.user)
        conversation, created = Conversation.objects.get_or_create(
            customer=request.user,
            technician=past_job.technician,
            defaults={"status": "chat_opened"},
        )
        return Response(
            {
                "conversation_id": str(conversation.id),
                "technician_id": str(past_job.technician.id),
                "business_name": past_job.technician.business_name,
                "message": "Re-booked successfully. Chat thread opened.",
            },
            status=status.HTTP_200_OK,
        )


class ConfirmJobCompletionView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request, id):
        job = get_object_or_404(JobBooking, id=id, customer=request.user)
        serializer = ConfirmJobCompletionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data["completed"]:
            job.status = "completed"
            job.completed_at = timezone.now()
            job.save(update_fields=["status", "completed_at"])

            # Increment technician completed jobs
            tech = job.technician
            tech.completed_jobs = JobBooking.objects.filter(technician=tech, status="completed").count()
            tech.update_reputation_and_badge()

        return Response({"status": job.status, "completed": True}, status=status.HTTP_200_OK)


class SubmitReviewView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request, id):
        job = get_object_or_404(JobBooking, id=id, customer=request.user)
        serializer = SubmitReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        review, _ = JobReview.objects.update_or_create(
            booking=job,
            defaults={
                "customer": request.user,
                "technician": job.technician,
                "rating": data["rating"],
                "comment": data.get("comment", ""),
                "photo_url": data.get("photo_url", ""),
            },
        )

        return Response(
            {
                "review_id": str(review.id),
                "rating": review.rating,
                "comment": review.comment,
                "photo_url": review.photo_url,
                "message": "Review submitted successfully.",
            },
            status=status.HTTP_201_CREATED,
        )
