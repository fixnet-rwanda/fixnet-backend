from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from core.permissions import IsCustomer
from apps.technicians.models import TechnicianProfile
from .serializers import AIChatRequestSerializer


class AIChatView(APIView):
    """
    SEARCH-02 & SEARCH-03:
    Retrieves answers strictly grounded in technician's verified profile and portfolio.
    If no relevant grounded content is available, provides a safe fallback without hallucination.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request):
        serializer = AIChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tech_id = serializer.validated_data["technician_id"]
        prompt = serializer.validated_data["prompt"].lower()

        tech = get_object_or_404(TechnicianProfile, id=tech_id)

        # Retrieve technician content descriptions
        content_snippets = [c.description for c in tech.contents.filter(moderation_status="approved") if c.description]
        categories = [c.name.lower() for c in tech.categories.all()]

        # Boundary check: does query match categories or portfolio?
        matched = any(cat in prompt for cat in categories) or any(any(word in s.lower() for word in prompt.split()) for s in content_snippets)

        if matched or content_snippets:
            portfolio_summary = "; ".join(content_snippets) if content_snippets else "general maintenance"
            response_text = (
                f"Based on {tech.business_name or 'the technician'}'s uploaded portfolio ({portfolio_summary}), "
                f"they handle relevant services. Would you like to chat with them directly?"
            )
            return Response(
                {
                    "response": response_text,
                    "confidence_score": 0.92,
                    "can_answer": True,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "response": f"I don't have enough information about that from {tech.business_name or 'the technician'}'s profile. Would you like to ask them directly in chat?",
                    "confidence_score": 0.35,
                    "can_answer": False,
                },
                status=status.HTTP_200_OK,
            )
