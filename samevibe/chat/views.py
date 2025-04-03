from django.shortcuts import render
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import generics, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from .models import Chats, Contents
from .serializer import ChatSerializer, ContentSerializer


class ChatAPIView(
    mixins.CreateModelMixin, mixins.ListModelMixin, generics.GenericAPIView
):

    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Chats.objects.filter(Q(user1=user) | Q(user2=user))

    def get(self, request, *args, **kwargs):

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get("to_user")
        if not to_user_id:
            return Response(
                {"detail": "Необходимо указать получателя заявки."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from_user = request.user

        existing_chat = Chats.objects.filter(
            Q(user1=from_user, user2_id=to_user_id)
            | Q(user1_id=to_user_id, user2=from_user)
        ).first()

        if existing_chat:
            serializer = self.get_serializer(existing_chat)
            return Response(serializer.data, status=status.HTTP_200_OK)

        data = {"user1": from_user.id, "user2": to_user_id}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        chanell_layer = get_channel_layer()
        other_user_id = to_user_id

        chat_data = {"message": "Новый чат создан", "chat": serializer.data}

        async_to_sync(chanell_layer.group_send)(
            f"chat_list_updates_{other_user_id}",
            {"type": "chat_update", "data": chat_data},
        )

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class ChatContentAPIView(generics.ListAPIView):
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs.get("chat_id")
        return Contents.objects.filter(chat_id=chat_id).order_by("created_at")


class ContentRetriveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contents.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sender != request.user:
            return Response(
                {"detail": "Нет доступа для редактирования этого сообщения."},
                status=403,
            )
        return super().update(request, *args, **kwargs)
