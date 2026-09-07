from django.urls import path
from .views import RespondQuoteView

urlpatterns = [
    path("<uuid:id>/respond", RespondQuoteView.as_view(), name="quote-respond"),
]
