from django.urls import path
from .views import (
    InitiateConversationView,
    ConversationListView,
    ConversationMessagesView,
    SendQuoteView,
)

urlpatterns = [
    path("", InitiateConversationView.as_view(), name="conversation-initiate"),
    path("list", ConversationListView.as_view(), name="conversation-list"),
    path("<uuid:id>/messages", ConversationMessagesView.as_view(), name="conversation-messages"),
    path("<uuid:id>/quotes", SendQuoteView.as_view(), name="conversation-send-quote"),
]
