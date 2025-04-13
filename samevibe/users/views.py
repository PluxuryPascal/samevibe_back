from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
import cloudinary
import cloudinary.utils
import time

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


class AvatarSignatureAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        folder = f"avatars/{request.user.id}"
        timestamp = int(time.time())
        params = {
            "timestamp": timestamp,
            "folder": folder,
            "width": 200,
            "height": 200,
            "crop": "fill",
            "gravity": "face",
            "quality": "auto",
            "fetch_format": "auto",
            "radius": "max",
        }

        signature = cloudinary.utils.api_sign_request(
            params, cloudinary.config().api_secret
        )
        params["signature"] = signature
        params["cloud_name"] = cloudinary.config().cloud_name
        return Response(params)
