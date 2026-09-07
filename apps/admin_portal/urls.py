from django.urls import path
from .views import (
    VerifyTechnicianView,
    ModerateContentView,
    DisputeRefundView,
    PricingConfigView,
    RevenueReportCSVView,
    SuspendUserView,
)

urlpatterns = [
    path("technicians/<uuid:id>/verify", VerifyTechnicianView.as_view(), name="admin-verify-technician"),
    path("content/<uuid:id>", ModerateContentView.as_view(), name="admin-moderate-content"),
    path("disputes/<uuid:id>/refund", DisputeRefundView.as_view(), name="admin-dispute-refund"),
    path("config/pricing", PricingConfigView.as_view(), name="admin-config-pricing"),
    path("reports/revenue", RevenueReportCSVView.as_view(), name="admin-report-revenue"),
    path("users/<uuid:id>/suspend", SuspendUserView.as_view(), name="admin-suspend-user"),
]
