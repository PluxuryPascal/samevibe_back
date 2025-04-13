import os
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
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


class UserRegisterAPIView(generics.CreateAPIView):

    queryset = Profile.objects.all()
    serializer_class = ProfileRegisterSerializer
    permission_classes = [
        AllowAny,
    ]


class InterestUserSearchAPIView(generics.ListAPIView):
    serializer_class = InterestMatchedUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        return User.objects.exclude(id=current_user.id)


class HobbyUserSearchAPIView(generics.ListAPIView):
    serializer_class = HobbyMatchedUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        return User.objects.exclude(id=current_user.id)


class MusicUserSearchAPIView(generics.ListAPIView):
    serializer_class = MusicMatchedUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        return User.objects.exclude(id=current_user.id)


class UserIdApiView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserIdSerializer

    def get_object(self):
        return self.request.user


logger = logging.getLogger(__name__)


class AvatarSignatureAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Проверяем конфигурацию Cloudinary
            if not all(
                [
                    os.environ.get("CLOUDINARY_API_NAME"),
                    os.environ.get("CLOUDINARY_API_KEY"),
                    os.environ.get("CLOUDINARY_API_SECRET"),
                ]
            ):
                raise ValueError("Cloudinary credentials not configured")

            # Генерируем обязательные параметры
            user_id = request.user.id
            timestamp = int(time.time())
            folder = f"avatars/{user_id}"

            # Базовые параметры для подписи
            params = {
                "timestamp": timestamp,
                "folder": folder,
                "upload_preset": "your_upload_preset",  # Укажите ваш preset
            }

            # Генерируем подпись
            signature = cloudinary.utils.api_sign_request(
                params, settings.CLOUDINARY_API_SECRET
            )

            return Response(
                {
                    "signature": signature,
                    "timestamp": timestamp,
                    "folder": folder,
                    "cloud_name": os.environ.get("CLOUDINARY_API_NAME"),
                    "api_key": os.environ.get("CLOUDINARY_API_KEY"),
                    "transformation": "c_fill,g_face,w_200,h_200,q_auto,f_auto,r_20",
                }
            )

        except Exception as e:
            logger.error(f"Signature generation failed: {str(e)}")
            return Response({"error": "Internal server error"}, status=500)
