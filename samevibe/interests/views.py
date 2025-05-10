from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, views, status, mixins
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from .models import Interest, Hobby, MusicGenre, UserInterest, UserHobby, UserMusic
from .serializer import (
    InterestSerializer,
    HobbySerializer,
    MusicGenreSerializer,
    UserInterestSerializer,
    UserHobbiesSerializer,
    UserMusicSerializer,
)


@method_decorator(cache_page(60 * 60), name="dispatch")
class InterestsAPIList(generics.ListAPIView):
    """
    Retrieve a list of all available interests.

    Returns:
        Response: A DRF Response containing a serialized list of all Interest objects.
    """

    queryset = Interest.objects.all()
    serializer_class = InterestSerializer


@method_decorator(cache_page(60 * 60), name="dispatch")
class HobbyAPIList(generics.ListAPIView):
    """
    Retrieve a list of all available hobbies.

    Returns:
        Response: A DRF Response containing a serialized list of all Hobby objects.
    """

    queryset = Hobby.objects.all()
    serializer_class = HobbySerializer


@method_decorator(cache_page(60 * 60), name="dispatch")
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
    CACHE_TIMEOUT = 60 * 60

    def get_queryset(self):
        """
        Returns:
            QuerySet: A queryset of UserInterest objects filtered by the authenticated user.
        """

        return UserInterest.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        uid = request.user.id
        cache_key = f"user_interests_{uid}"
        data = cache.get(cache_key)
        if data is None:
            qs = UserInterest.objects.filter(user=request.user)
            data = UserInterestSerializer(qs, many=True).data
            cache.set(cache_key, data, self.CACHE_TIMEOUT)
        return Response(data)

    def get(self, request, *args, **kwargs):
        """
        Retrieve the list of interests associated with the current user.
        """

        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        Bulk update or create the interests associated with the current user.

        The request body should be a JSON object containing an array of interest IDs:
            { "interest_ids": [1, 3, 5] }

        Returns:
            Response: A DRF Response with a success message if updated or created, or error details.
        """
        interest_ids = request.data.get("interest_ids", [])
        user = request.user

        # Проверяем, что все переданные интересы существуют
        interests = Interest.objects.filter(id__in=interest_ids)
        if interests.count() != len(interest_ids):
            return Response(
                {"detail": "Некоторые интересы не найдены."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Обновление: удаляем все старые связи и создаём новые
        UserInterest.objects.filter(user=user).delete()
        new_records = [
            UserInterest(user=user, interest_id=interest_id)
            for interest_id in interest_ids
        ]
        UserInterest.objects.bulk_create(new_records)

        uid = request.user.id
        cache.delete(f"profile_{uid}")
        cache.delete(f"user_interests_{uid}")
        cache.delete(f"user_interest_search_{uid}")
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
    CACHE_TIMEOUT = 60 * 60

    def get_queryset(self):
        """
        Returns:
            QuerySet: A queryset of UserHobby objects filtered by the authenticated user.
        """
        return UserHobby.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        uid = request.user.id
        cache_key = f"user_hobbies_{uid}"
        data = cache.get(cache_key)
        if data is None:
            qs = UserHobby.objects.filter(user=request.user)
            data = UserHobbiesSerializer(qs, many=True).data
            cache.set(cache_key, data, self.CACHE_TIMEOUT)
        return Response(data)

    def get(self, request, *args, **kwargs):
        """
        Retrieve the list of hobbies associated with the current user.
        """

        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        Bulk update or create the hobbies associated with the current user.

        The request body should be a JSON object containing an array of hobbies IDs:
            { "hobby_ids": [1, 3, 5] }

        Returns:
            Response: A DRF Response with a success message if updated or created, or error details.
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
        new_records = [
            UserHobby(user=user, hobby_id=hobby_id) for hobby_id in hobby_ids
        ]
        UserHobby.objects.bulk_create(new_records)

        uid = request.user.id
        cache.delete(f"profile_{uid}")
        cache.delete(f"user_hobbies_{uid}")
        cache.delete(f"user_hobby_search_{uid}")

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
    CACHE_TIMEOUT = 60 * 60

    def get_queryset(self):
        """
        Returns:
            QuerySet: A queryset of UserMusic objects filtered by the authenticated user.
        """

        return UserMusic.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        uid = request.user.id
        cache_key = f"user_music_{uid}"
        data = cache.get(cache_key)
        if data is None:
            qs = UserMusic.objects.filter(user=request.user)
            data = UserMusicSerializer(qs, many=True).data
            cache.set(cache_key, data, self.CACHE_TIMEOUT)
        return Response(data)

    def get(self, request, *args, **kwargs):
        """
        Retrieve the list of music genres associated with the current user.
        """

        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        Bulk update or create the musics associated with the current user.

        The request body should be a JSON object containing an array of musics IDs:
            { "music_ids": [1, 3, 5] }

        Returns:
            Response: A DRF Response with a success message if updated or created, or error details.
        """
        music_ids = request.data.get("music_ids", [])
        user = request.user

        musics = MusicGenre.objects.filter(id__in=music_ids)
        if musics.count() != len(music_ids):
            return Response(
                {"detail": "Некоторые жанры не найдены."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        UserMusic.objects.filter(user=user).delete()
        new_records = [
            UserMusic(user=user, genre_id=genre_id) for genre_id in music_ids
        ]
        UserMusic.objects.bulk_create(new_records)

        uid = request.user.id
        cache.delete(f"profile_{uid}")
        cache.delete(f"user_music_{uid}")
        cache.delete(f"user_music_search_{uid}")

        return Response({"detail": "Жанры обновлены."}, status=status.HTTP_200_OK)
