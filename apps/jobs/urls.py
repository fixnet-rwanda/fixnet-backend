from django.urls import path
from .views import (
    JobHistoryView,
    OneTapRebookView,
    ConfirmJobCompletionView,
    SubmitReviewView,
)

urlpatterns = [
    path("history", JobHistoryView.as_view(), name="job-history"),
    path("<uuid:id>/rebook", OneTapRebookView.as_view(), name="job-rebook"),
    path("<uuid:id>/complete", ConfirmJobCompletionView.as_view(), name="job-complete"),
    path("<uuid:id>/reviews", SubmitReviewView.as_view(), name="job-reviews"),
]
