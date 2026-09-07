from django.urls import path
from .views import TechnicianSubscriptionPaymentView

urlpatterns = [
    path("subscribe", TechnicianSubscriptionPaymentView.as_view(), name="subscription-subscribe"),
]
