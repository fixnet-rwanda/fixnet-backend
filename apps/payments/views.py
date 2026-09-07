import uuid
import io
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.permissions import IsCustomer, IsTechnician
from apps.conversations.models import Quote, Message
from apps.jobs.models import JobBooking
from .models import PaymentTransaction, TechnicianSubscription
from .serializers import (
    BookingDepositSerializer,
    WebhookSerializer,
    SubscriptionPaymentSerializer,
)


class PayBookingDepositView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request):
        serializer = BookingDepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quote_id = serializer.validated_data["quote_id"]
        quote = get_object_or_404(Quote, id=quote_id)

        tx_ref = f"tx_momo_{uuid.uuid4().hex[:8]}"
        tx = PaymentTransaction.objects.create(
            transaction_ref=tx_ref,
            quote=quote,
            payer=request.user,
            amount_rwf=quote.required_booking_deposit_rwf,
            payment_method=serializer.validated_data["payment_method"],
            phone_number=serializer.validated_data["phone_number"],
            status="pending",
        )

        return Response(
            {
                "transaction_id": tx.transaction_ref,
                "status": "pending",
                "user_instruction": "Approve the MoMo USSD prompt on your phone.",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = WebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tx = PaymentTransaction.objects.filter(transaction_ref=data["transaction_id"]).first()
        if not tx:
            # Staging mock creation if not existing
            quote = None
            if "quote_id" in data:
                quote = Quote.objects.filter(id=data["quote_id"]).first()
            if not quote:
                return Response({"error_code": "RESOURCE_NOT_FOUND", "message": "Transaction or quote not found."}, status=status.HTTP_404_NOT_FOUND)
            tx = PaymentTransaction.objects.create(
                transaction_ref=data["transaction_id"],
                quote=quote,
                payer=quote.conversation.customer,
                amount_rwf=data["amount_rwf"],
                status=data["status"],
            )

        with transaction.atomic():
            tx.status = data["status"]
            tx.save(update_fields=["status"])

            if tx.status == "successful" and tx.quote:
                conv = tx.quote.conversation
                conv.contact_unlocked = True
                conv.save(update_fields=["contact_unlocked"])

                # Post system message into conversation revealing technician's phone number
                tech_phone = conv.technician.user.phone_number or "Available in technician profile"
                Message.objects.create(
                    conversation=conv,
                    sender=None,
                    sender_type="system",
                    content=f"Booking deposit paid successfully. Technician contact unlocked: {tech_phone}",
                )

                # Update job booking status
                booking = JobBooking.objects.filter(quote=tx.quote).first()
                if booking:
                    booking.status = "deposit_paid"
                    booking.unlocked_at = timezone.now()
                    booking.save(update_fields=["status", "unlocked_at"])

        return Response({"status": "received", "transaction_status": tx.status}, status=status.HTTP_200_OK)


class PaymentReceiptView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        tx = get_object_or_404(PaymentTransaction, transaction_ref=id)

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.drawString(100, 750, "FIXNET - PAYMENT RECEIPT")
            p.drawString(100, 720, f"Transaction Ref: {tx.transaction_ref}")
            p.drawString(100, 700, f"Date: {tx.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            p.drawString(100, 680, f"Payer Phone: {tx.phone_number}")
            p.drawString(100, 660, f"Amount Paid: {tx.amount_rwf} RWF")
            p.drawString(100, 640, f"Status: {tx.status.upper()}")
            p.drawString(100, 600, "Thank you for using FixNet!")
            p.showPage()
            p.save()
            buffer.seek(0)
            return HttpResponse(buffer, content_type="application/pdf")
        except ImportError:
            # Fallback simple text-based pdf simulation
            receipt_content = f"FIXNET RECEIPT\nRef: {tx.transaction_ref}\nAmount: {tx.amount_rwf} RWF\nStatus: {tx.status}"
            response = HttpResponse(receipt_content, content_type="text/plain")
            response["Content-Disposition"] = f'attachment; filename="receipt_{tx.transaction_ref}.txt"'
            return response


class TechnicianSubscriptionPaymentView(APIView):
    permission_classes = [IsAuthenticated, IsTechnician]

    def post(self, request):
        profile = getattr(request.user, "technician_profile", None)
        if not profile:
            return Response({"error_code": "RESOURCE_NOT_FOUND", "message": "Technician profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubscriptionPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subscription = TechnicianSubscription.objects.create(
            technician=profile,
            plan_id=serializer.validated_data["plan_id"],
            status="active",
            start_date=timezone.now(),
            expires_at=timezone.now() + timezone.timedelta(days=30),
        )
        profile.subscription_status = "active"
        profile.is_searchable = True
        profile.save(update_fields=["subscription_status", "is_searchable"])

        return Response(
            {
                "status": "active",
                "subscription_id": str(subscription.id),
                "plan_id": subscription.plan_id,
                "expires_at": subscription.expires_at.isoformat(),
            },
            status=status.HTTP_200_OK,
        )
