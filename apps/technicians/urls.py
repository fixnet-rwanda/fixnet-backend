from django.urls import path
from .views import (
    TechnicianRegisterView,
    TechnicianListView,
    TechnicianDetailView,
    TechnicianContentUploadView,
    TechnicianDashboardView,
    CompleteTrainingView,
)

urlpatterns = [
    path("", TechnicianListView.as_view(), name="technician-list"),
    path("register", TechnicianRegisterView.as_view(), name="technician-register"),
    path("me/content", TechnicianContentUploadView.as_view(), name="technician-content-upload"),
    path("me/dashboard", TechnicianDashboardView.as_view(), name="technician-dashboard"),
    path("me/onboarding-complete", CompleteTrainingView.as_view(), name="technician-onboarding-complete"),
    path("<uuid:id>", TechnicianDetailView.as_view(), name="technician-detail"),
]
