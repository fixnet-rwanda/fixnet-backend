from django.urls import path
from .views import CurrentUserView, UpdateLanguageView

urlpatterns = [
    path("me", CurrentUserView.as_view(), name="user-me"),
    path("me/language", UpdateLanguageView.as_view(), name="user-language"),
]
