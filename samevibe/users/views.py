import os
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

import cloudinary
import cloudinary.utils
import time
import logging


from django.conf import settings

from .models import Profile
from .serializer import (
    ProfileSerializer,
    ProfileRegisterSerializer,
    InterestMatchedUserSerializer,
    HobbyMatchedUserSerializer,
    MusicMatchedUserSerializer,
    UserIdSerializer,
)


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating the profile of the authenticated user.

    Supports:
      - GET: Retrieve the current user's profile data.
      - PUT/PATCH: Update the current user's profile.

    The profile includes fields such as user's first name, last name, email (nested in user),
    as well as additional profile fields like photo and gender.

    Returns:
        Response: A DRF Response containing the serialized profile data.
    """

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieve the profile object associated with the authenticated user.

        Returns:
            Profile: The Profile instance linked to the current user.
        """

        return Profile.objects.get(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        key = f"profile_{request.user.id}"
        data = cache.get(key)
        if data:
            return Response(data)
        resp = super().retrieve(request, *args, **kwargs)
        cache.set(key, resp.data, 10 * 60)
        return resp

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete(f"profile_{instance.user.id}")


class UserRegisterAPIView(generics.CreateAPIView):
    """
    Endpoint for user registration.

    Provides:
      - POST /api/users/register/ to create a new user profile.

    Anyone (authenticated or not) can register.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileRegisterSerializer
    permission_classes = [
        AllowAny,
    ]


class InterestUserSearchAPIView(generics.ListAPIView):
    """
    List users matched by interest.

    This endpoint returns a list of all users except the authenticated one,
    to enable matching on interests.

    Requires authentication.
    """

    serializer_class = InterestMatchedUserSerializer
    permission_classes = [IsAuthenticated]
    CACHE_TIMEOUT = 5 * 60

    def get_queryset(self):
        """
        Build queryset excluding the current user.

        Returns:
            QuerySet[User]: All users except request.user.
        """
        current_user = self.request.user
        return User.objects.exclude(id=current_user.id)

    def list(self, request, *args, **kwargs):
        uid = request.user.id
        cache_key = f"user_interest_ids_{uid}"
        user_ids = cache.get(cache_key)

        if user_ids is None:
            # Кэшируем только список id, без статусов
            user_ids = list(User.objects.exclude(id=uid).values_list("id", flat=True))
            cache.set(cache_key, user_ids, self.CACHE_TIMEOUT)

        # Загружаем свежие объекты и отдаем в сериализатор статус
        qs = User.objects.filter(id__in=user_ids)
        serializer = self.get_serializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class HobbyUserSearchAPIView(generics.ListAPIView):
    """
    List users matched by hobbies.

    This endpoint returns a list of all users except the authenticated one,
    to enable matching on hobbies.

    Requires authentication.
    """

    serializer_class = HobbyMatchedUserSerializer
    permission_classes = [IsAuthenticated]
    CACHE_TIMEOUT = 5 * 60

    def get_queryset(self):
        """
        Build queryset excluding the current user.

        Returns:
            QuerySet[User]: All users except request.user.
        """
        current_user = self.request.user
        return User.objects.exclude(id=current_user.id)

    def list(self, request, *args, **kwargs):
        uid = request.user.id
        cache_key = f"user_hobby_ids_{uid}"
        user_ids = cache.get(cache_key)

        if user_ids is None:
            # Кэшируем только список id, без статусов
            user_ids = list(User.objects.exclude(id=uid).values_list("id", flat=True))
            cache.set(cache_key, user_ids, self.CACHE_TIMEOUT)

        # Загружаем свежие объекты и отдаем в сериализатор статус
        qs = User.objects.filter(id__in=user_ids)
        serializer = self.get_serializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class MusicUserSearchAPIView(generics.ListAPIView):
    """
    List users matched by music preferences.

    This endpoint returns a list of all users except the authenticated one,
    to enable matching on music tastes.

    Requires authentication.
    """

    serializer_class = MusicMatchedUserSerializer
    permission_classes = [IsAuthenticated]
    CACHE_TIMEOUT = 5 * 60

    def get_queryset(self):
        """
        Build queryset excluding the current user.

        Returns:
            QuerySet[User]: All users except request.user.
        """
        current_user = self.request.user
        return User.objects.exclude(id=current_user.id)

    def list(self, request, *args, **kwargs):
        uid = request.user.id
        cache_key = f"user_music_ids_{uid}"
        user_ids = cache.get(cache_key)

        if user_ids is None:
            # Кэшируем только список id, без статусов
            user_ids = list(User.objects.exclude(id=uid).values_list("id", flat=True))
            cache.set(cache_key, user_ids, self.CACHE_TIMEOUT)

        # Загружаем свежие объекты и отдаем в сериализатор статус
        qs = User.objects.filter(id__in=user_ids)
        serializer = self.get_serializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class UserIdApiView(generics.RetrieveAPIView):
    """
    Retrieve the authenticated user's ID.

    Provides:
      - GET /api/users/me/ to fetch the current user's ID.

    Requires authentication.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserIdSerializer

    def get_object(self):
        """
        Return the user instance for the requester.

        Returns:
            User: The authenticated user.
        """
        return self.request.user


logger = logging.getLogger(__name__)


class AvatarSignatureAPIView(APIView):
    """
    Generate a Cloudinary upload signature for user avatars.

    Provides:
      - GET /api/avatar-signature/

    It verifies Cloudinary settings, prepares the upload
    folder (`avatars/{user_id}`), signs parameters, and returns them.
    Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Create and return a Cloudinary signature for avatar upload.

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
            user_id = request.user.id
            folder = f"avatars/{user_id}"

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
            logger.error(f"Signature generation failed: {e}")
            return Response({"error": "Internal server error"}, status=500)
