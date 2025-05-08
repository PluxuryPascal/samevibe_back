from django.shortcuts import render
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import generics, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.views import APIView
import time
import cloudinary
import cloudinary.utils
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from django.conf import settings

from .models import Chats, Contents
from .serializer import ChatSerializer, ContentSerializer


class ChatAPIView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    generics.GenericAPIView,
):
    """
    API ViewSet for managing one-to-one chats.

    This view provides endpoints to:
      - List all chats involving the authenticated user.
      - Create a new chat between two users (or return an existing one).

    All operations require authentication.
    """

    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Build the queryset for listing chats.

        Returns:
            QuerySet[Chats]: All Chats where the authenticated user is either user1 or user2.
        """
        user = self.request.user
        return Chats.objects.filter(Q(user1=user) | Q(user2=user))

    def get(self, request, *args, **kwargs):
        """
        Retrieve the list of chats.

        This is an alias for `.list()` to satisfy ViewSet conventions.

        Args:
            request (Request): The incoming HTTP GET request.

        Returns:
            Response: Serialized list of the user's chats.
        """
        return self.list(request, *args, **kwargs)

    @method_decorator(cache_page(10 * 60), name="list")
    def list(self, request, *args, **kwargs):
        """
        List all chats for the authenticated user.

        This endpoint returns all chat threads involving the current user,
        serialized via `ChatSerializer`.

        Args:
            request (Request): The incoming HTTP GET request.

        Returns:
            Response: 200 OK with a JSON array of chat objects.
        """
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Create a new chat or return an existing one.

        If a chat between the authenticated user and `to_user` already exists,
        it will be returned. Otherwise, a new `Chats` instance is created.

        Request Body:
            to_user (int): ID of the user with whom to start the chat.

        Args:
            request (Request): The incoming HTTP POST request.

        Returns:
            Response: 201 CREATED with the new chat data, or 200 OK if it already existed.
        """
        to_user_id = request.data.get("to_user")
        if not to_user_id:
            return Response(
                {"detail": "Необходимо указать получателя чата."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        me = request.user
        # проверяем, есть ли уже чат между двумя пользователями
        existing = Chats.objects.filter(
            Q(user1=me, user2_id=to_user_id) | Q(user1_id=to_user_id, user2=me)
        ).first()
        if existing:
            ser = self.get_serializer(existing, context={"request": request})
            return Response(ser.data, status=status.HTTP_200_OK)

        # создаём новый чат
        data = {"user1": me.id, "user2": to_user_id}
        write_ser = self.get_serializer(data=data, context={"request": request})
        write_ser.is_valid(raise_exception=True)
        self.perform_create(write_ser)

        chat = write_ser.instance

        # отдадим «read» сериализатор
        read_ser = self.get_serializer(chat, context={"request": request})

        cl = get_channel_layer()
        for uid in (me.id, to_user_id):
            async_to_sync(cl.group_send)(
                f"chat_list_updates_{uid}",
                {"type": "chat_update", "data": read_ser.data},
            )

        cache.delete_pattern(f"*{request.user.id}*/api/v1/chat/chats*")
        cache.delete_pattern(f"*{to_user_id}*/api/v1/chat/chats*")
        return Response(read_ser.data, status=status.HTTP_201_CREATED)


class ChatContentAPIView(generics.ListAPIView):
    """
    Read-only endpoint to retrieve all messages in a specific chat.

    Provides:
      - GET /api/chats/{chat_id}/contents/ to list every message for the given chat,
        ordered by creation time.

    Requires authentication.
    """

    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Build queryset of Contents for a given chat.

        Returns:
            QuerySet[Contents]: All messages in the chat identified by `chat_id`.
        """
        chat_id = self.kwargs["chat_id"]
        return Contents.objects.filter(chat_id=chat_id).order_by("created_at")

    def list(self, request, *args, **kwargs):
        """
        Retrieve and serialize the chat's messages.

        Args:
            request (Request): The incoming HTTP GET request.

        Returns:
            Response: 200 OK with a JSON array of message objects.
        """
        qs = self.get_queryset()
        ser = self.get_serializer(qs, many=True, context={"request": request})
        return Response(ser.data)


class ContentRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    Endpoint for retrieving or updating a single chat message.

    Supports:
      - GET /api/contents/{pk}/ to fetch the message.
      - PATCH/PUT /api/contents/{pk}/ to edit it (author only).

    Requires authentication.
    """

    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Provide the base queryset for retrieve/update.

        Returns:
            QuerySet[Contents]: All messages, filtered later by `pk`.
        """
        return Contents.objects.all()

    def update(self, request, *args, **kwargs):
        """
        Edit an existing message if the requester is its author.

        Args:
            request (Request): The incoming HTTP PATCH/PUT request.
            kwargs (dict): URL kwargs including 'pk'.

        Returns:
            Response: 200 OK with updated data, or 403 FORBIDDEN / 404 NOT FOUND.
        """
        instance = self.get_object()
        if instance.sender != request.user:
            return Response(
                {"detail": "Нет доступа для редактирования этого сообщения."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)


class ChatAttachmentSignatureAPIView(APIView):
    """
    Generate a Cloudinary upload signature for chat attachments.

    Provides:
      - GET /api/chats/attachment-signature/?chat_id={chat_id}

    It verifies required Cloudinary settings, filters and signs the
    upload parameters, and returns a timestamped signature and folder.
    Authentication required.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Create and return a Cloudinary signature and safe folder path.

        Query Params:
            chat_id (str): Identifier of the chat for folder naming.

        Returns:
            Response: 200 OK with JSON {signature, timestamp, folder}, or
                      500 INTERNAL SERVER ERROR on failure.
        """
        try:
            # 1) Проверяем, что в настройках есть все ключи Cloudinary
            for var in (
                "CLOUDINARY_NAME",
                "CLOUDINARY_API_KEY",
                "CLOUDINARY_API_SECRET",
            ):
                if not getattr(settings, var, None):
                    raise ValueError(f"{var} not configured")

            # 2) Извлекаем реальные параметры из body.paramsToSign, если нужно
            raw = request.data.get("paramsToSign") or request.data

            # 3) Гарантируем безопасный folder (не подписываем его)
            chat_id = request.query_params.get("chat_id")
            folder = f"chat/{chat_id}/"

            # 4) Формируем словарь для подписи, исключая ненужные ключи
            params_to_sign = {
                k: v
                for k, v in raw.items()
                if v is not None
                and k
                not in ("file", "api_key", "resource_type", "cloud_name", "folder")
            }

            # 5) Подписываем именно эти параметры
            signature = cloudinary.utils.api_sign_request(
                params_to_sign, settings.CLOUDINARY_API_SECRET
            )

            # 6) Отдаём подпись, timestamp и безопасный folder
            return Response(
                {
                    "signature": signature,
                    "timestamp": params_to_sign.get("timestamp", int(time.time())),
                    "folder": folder,
                }
            )

        except Exception:
            return Response({"error": "Internal server error"}, status=500)
