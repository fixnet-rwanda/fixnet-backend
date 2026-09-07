from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from core.permissions import IsCustomer, IsTechnician
from apps.technicians.models import TechnicianProfile
from .models import Conversation, Message, Quote
from .serializers import (
    InitiateConversationSerializer,
    ConversationListSerializer,
    MessageSerializer,
    CreateQuoteSerializer,
    RespondQuoteSerializer,
)


class InitiateConversationView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request):
        serializer = InitiateConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tech_id = serializer.validated_data["technician_id"]

        technician = get_object_or_404(TechnicianProfile, id=tech_id)
        conversation, created = Conversation.objects.get_or_create(
            customer=request.user,
            technician=technician,
            defaults={"status": "chat_opened"},
        )

        return Response(
            {
                "conversation_id": str(conversation.id),
                "status": conversation.status,
            },
            status=status.HTTP_201_CREATED,
        )


class ConversationListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationListSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == "customer":
            return Conversation.objects.filter(customer=user).order_by("-updated_at")
        elif user.role == "technician" and hasattr(user, "technician_profile"):
            return Conversation.objects.filter(technician=user.technician_profile).order_by("-updated_at")
        elif user.role in ("support_agent", "system_admin"):
            return Conversation.objects.all().order_by("-updated_at")
        return Conversation.objects.none()


class ConversationMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        conversation = get_object_or_404(Conversation, id=id)
        # Authorization: user must be participant or admin
        if request.user != conversation.customer and getattr(request.user, "technician_profile", None) != conversation.technician:
            if request.user.role not in ("support_agent", "system_admin"):
                return Response({"error_code": "PERMISSION_DENIED", "message": "Not a participant in this conversation."}, status=status.HTTP_403_FORBIDDEN)

        messages = conversation.messages.order_by("created_at")
        serializer = MessageSerializer(messages, many=True)
        return Response({"messages": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, id):
        conversation = get_object_or_404(Conversation, id=id)
        sender_type = "customer" if request.user == conversation.customer else "technician"

        content = request.data.get("content", "").strip()
        if not content:
            return Response({"error_code": "VALIDATION_ERROR", "message": "Message content cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            sender_type=sender_type,
            content=content,
        )

        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)


class SendQuoteView(APIView):
    permission_classes = [IsAuthenticated, IsTechnician]

    def post(self, request, id):
        conversation = get_object_or_404(Conversation, id=id)
        profile = getattr(request.user, "technician_profile", None)
        if not profile or conversation.technician != profile:
            return Response({"error_code": "PERMISSION_DENIED", "message": "Only the assigned technician can quote."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quote = Quote.objects.create(
            conversation=conversation,
            technician=profile,
            total_price_rwf=serializer.validated_data["total_price_rwf"],
            scope_notes=serializer.validated_data["scope_notes"],
            status="sent",
        )

        return Response(
            {
                "quote_id": str(quote.id),
                "status": quote.status,
            },
            status=status.HTTP_201_CREATED,
        )


class RespondQuoteView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request, id):
        quote = get_object_or_404(Quote, id=id)
        if quote.conversation.customer != request.user:
            return Response({"error_code": "PERMISSION_DENIED", "message": "Only the booking customer can respond to this quote."}, status=status.HTTP_403_FORBIDDEN)

        if quote.status == "expired" or (quote.expires_at and quote.expires_at < timezone.now()):
            quote.status = "expired"
            quote.save(update_fields=["status"])
            return Response({"error_code": "BUSINESS_RULE_VIOLATION", "message": "This quote has expired. Please request a new quote."}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        serializer = RespondQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data["action"]

        if action == "accept":
            quote.status = "quote_accepted"
            quote.save(update_fields=["status"])

            # Create or update JobBooking in apps.jobs
            from apps.jobs.models import JobBooking
            JobBooking.objects.get_or_create(
                quote=quote,
                defaults={
                    "customer": request.user,
                    "technician": quote.technician,
                    "service_category": quote.technician.categories.first().name if quote.technician.categories.exists() else "General Repair",
                    "deposit_amount_rwf": quote.required_booking_deposit_rwf,
                    "status": "quote_accepted",
                },
            )

            return Response(
                {
                    "status": "quote_accepted",
                    "required_booking_deposit_rwf": quote.required_booking_deposit_rwf,
                    "payment_next_step_url": "/v1/payments/booking-deposit",
                },
                status=status.HTTP_200_OK,
            )
        else:
            quote.status = "declined"
            quote.save(update_fields=["status"])
            return Response({"status": "quote_declined"}, status=status.HTTP_200_OK)
