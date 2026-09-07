from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({"status": "healthy", "service": "fixnet-backend", "version": "v1"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),

    # v1 REST API Routes
    path("v1/auth/", include("apps.users.urls_auth")),
    path("v1/users/", include("apps.users.urls")),
    path("v1/technicians/", include("apps.technicians.urls")),
    path("v1/conversations/", include("apps.conversations.urls")),
    path("v1/quotes/", include("apps.conversations.urls_quotes")),
    path("v1/ai/", include("apps.ai_assistant.urls")),
    path("v1/payments/", include("apps.payments.urls_payments")),
    path("v1/subscriptions/", include("apps.payments.urls_subscriptions")),
    path("v1/jobs/", include("apps.jobs.urls")),
    path("v1/admin/", include("apps.admin_portal.urls")),
]
