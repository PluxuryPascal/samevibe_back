from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, views, status, mixins
from rest_framework.response import Response

from .models import Interest, Hobby, MusicGenre, UserInterest, UserHobby, UserMusic
from .serializer import (
    InterestSerializer,
    HobbySerializer,
    MusicGenreSerializer,
    UserInterestSerializer,
    UserHobbiesSerializer,
    UserMusicSerializer,
)


class InterestsAPIList(generics.ListAPIView):
    """
    Retrieve a list of all available interests.

    Returns:
        Response: A DRF Response containing a serialized list of all Interest objects.
    """

    queryset = Interest.objects.all()
    serializer_class = InterestSerializer


class HobbyAPIList(generics.ListAPIView):
    """
    Retrieve a list of all available hobbies.

    Returns:
        Response: A DRF Response containing a serialized list of all Hobby objects.
    """

    queryset = Hobby.objects.all()
    serializer_class = HobbySerializer


class MusicGenreAPIList(generics.ListAPIView):
    """
    Retrieve a list of all available music genres.

    Returns:
        Response: A DRF Response containing a serialized list of all MusicGenre objects.
    """

    queryset = MusicGenre.objects.all()
    serializer_class = MusicGenreSerializer


class UserInterestAPIView(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """
    API view for managing the interests associated with the authenticated user.

    Supports the following HTTP methods:
      - GET: Retrieve the list of interests associated with the current user.
      - POST: Create a new user-interest association.
      - PATCH: Bulk update the interests for the current user.

    Expected JSON for PATCH:
      {
          "interest_ids": [1, 3, 5]
      }

    Attributes:
        serializer_class: The serializer class for UserInterest.
    """

    serializer_class = UserInterestSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        """
        Returns:
            QuerySet: A queryset of UserInterest objects filtered by the authenticated user.
        """

        return UserInterest.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        """
        Retrieve the list of interests associated with the current user.
        """

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Create a new user-interest association for the current user.

        The request should include the interest ID in the field 'interest_id'.

        Returns:
            Response: A DRF Response with the created object data.
        """

        return self.create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Bulk update the interests associated with the current user.

        The request body should be a JSON object containing an array of interest IDs:
            { "interest_ids": [1, 3, 5] }

        Returns:
            Response: A DRF Response with a success message if updated, or error details.
        """

        interest_ids = request.data.get("interest_ids", [])
        user = request.user

        interests = Interest.objects.filter(id__in=interest_ids)
        if interests.count() != len(interest_ids):
            return Response(
                {"detail": "Некоторые интересы не найдены."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        UserInterest.objects.filter(user=user).delete()
        for interest_id in interest_ids:
            UserInterest.objects.create(user=user, interest_id=interest_id)

        return Response({"detail": "Интересы обновлены."}, status=status.HTTP_200_OK)


class UserHobbyAPIView(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """
    API view for managing the hobbies associated with the authenticated user.

    Supports:
      - GET: Retrieve the list of hobbies for the current user.
      - POST: Create a new user-hobby association.
      - PATCH: Bulk update the hobbies for the current user.

    Expected JSON for PATCH:
      {
          "hobby_ids": [2, 4, 6]
      }

    Attributes:
        serializer_class: The serializer class for UserHobby.
    """

    serializer_class = UserHobbiesSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        """
        Returns:
            QuerySet: A queryset of UserHobby objects filtered by the authenticated user.
        """
        return UserHobby.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        """
        Retrieve the list of hobbies associated with the current user.
        """

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Create a new user-hobby association for the current user.

        Returns:
            Response: A DRF Response with the created object data.
        """

        return self.create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Bulk update the hobbies associated with the current user.

        The request body should contain a JSON object with a key 'hobby_ids':
            { "hobby_ids": [2, 4, 6] }

        Returns:
            Response: A DRF Response with a success message or error details.
        """

        hobby_ids = request.data.get("hobby_ids", [])
        user = request.user

        hobbies = Hobby.objects.filter(id__in=hobby_ids)

        if hobbies.count() != len(hobby_ids):
            return Response(
                {"detail": "Некоторые хобби не найдены."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        UserHobby.objects.filter(user=user).delete()
        for hobby_id in hobby_ids:
            UserHobby.objects.create(user=user, hobby_id=hobby_id)

        return Response({"detail": "Хобби обновлены."}, status=status.HTTP_200_OK)


class UserMusicAPIView(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """
    API view for managing the music genres associated with the authenticated user.

    Supports:
      - GET: Retrieve the list of music genres for the current user.
      - POST: Create a new user-music association.
      - PATCH: Bulk update the music genres for the current user.

    Expected JSON for PATCH:
      {
          "music_ids": [1, 2, 3]
      }

    Attributes:
        serializer_class: The serializer class for UserMusic.
    """

    serializer_class = UserMusicSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        """
        Returns:
            QuerySet: A queryset of UserMusic objects filtered by the authenticated user.
        """

        return UserMusic.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        """
        Retrieve the list of music genres associated with the current user.
        """

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Create a new user-music association for the current user.

        Returns:
            Response: A DRF Response with the created object data.
        """

        return self.create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Bulk update the music genres associated with the current user.

        The request body should contain a JSON object with a key 'music_ids':
            { "music_ids": [1, 2, 3] }

        Returns:
            Response: A DRF Response with a success message or error details.
        """

        music_ids = request.data.get("music_ids", [])
        user = request.user

        musics = MusicGenre.objects.filter(id__in=music_ids)

        if musics.count() != len(music_ids):
            return Response(
                {"detail": "Некоторые музыкальные жанры не найдены."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        UserMusic.objects.filter(user=user).delete()
        for music_id in music_ids:
            UserMusic.objects.create(user=user, music_id=music_id)
        return Response(
            {"detail": "Музыкальные жанры обновлены."}, status=status.HTTP_200_OK
        )
