from django.urls import path
from .views import ChatAPIView, ChatContentAPIView, ContentRetriveUpdateAPIView

urlpatterns = [
    path("chats/", ChatAPIView.as_view(), name="chats"),
    path(
        "chats/<int:chat_id>/messages/",
        ChatContentAPIView.as_view(),
        name="chat-contents",
    ),
    path(
        "messages/<int:pk>/",
        ContentRetriveUpdateAPIView.as_view(),
        name="contents-detail",
    ),
]
