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

from django.conf import settings

from .models import Chats, Contents
from .serializer import ChatSerializer, ContentSerializer


class ChatAPIView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    generics.GenericAPIView,
):
    """
    GET  /api/chats/         — список чатов пользователя
    POST /api/chats/         — создать чат (или вернуть существующий)
    """

    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Chats.objects.filter(Q(user1=user) | Q(user2=user))

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
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

        return Response(read_ser.data, status=status.HTTP_201_CREATED)


class ChatContentAPIView(generics.ListAPIView):
    """
    GET /api/chats/{chat_id}/contents/ — все сообщения в чате
    """

    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs["chat_id"]
        return Contents.objects.filter(chat_id=chat_id).order_by("created_at")

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        ser = self.get_serializer(qs, many=True, context={"request": request})
        return Response(ser.data)


class ContentRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/contents/{pk}/ — получить одно сообщение
    PATCH/PUT /api/contents/{pk}/ — отредактировать (только автору)
    """

    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contents.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sender != request.user:
            return Response(
                {"detail": "Нет доступа для редактирования этого сообщения."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)


class ChatAttachmentSignatureAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
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

        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)
