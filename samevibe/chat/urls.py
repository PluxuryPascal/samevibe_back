from django.urls import path
from .views import (
    ChatAPIView,
    ChatContentAPIView,
    ContentRetrieveUpdateAPIView,
    ChatAttachmentSignatureAPIView,
)

urlpatterns = [
    path("chats/", ChatAPIView.as_view(), name="chats"),
    path(
        "chats/<int:chat_id>/messages/",
        ChatContentAPIView.as_view(),
        name="chat-contents",
    ),
    path(
        "messages/<int:pk>/",
        ContentRetrieveUpdateAPIView.as_view(),
        name="contents-detail",
    ),
    path(
        "attachment-signature/",
        ChatAttachmentSignatureAPIView.as_view(),
        name="attachment-signature",
    ),
]
