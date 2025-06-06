from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from chat.models import Chats
from .models import Friendship
from .serializer import (
    FriendshipReadSerializer,
    FriendshipWriteSerializer,
)


class FriendshipAPIList(viewsets.ViewSet):
    """
    API ViewSet for managing friendship requests.

    This viewset allows an authenticated user to:
      - List all friendship records related to them, filtered by status.
      - Create a new friendship request (with status 'sended').
      - Update an existing friendship request (accept an incoming request).
      - Delete an existing friendship (cancel a request or remove a friend).

    All operations are secured with authentication.
    """

    permission_classes = [IsAuthenticated]
    CACHE_TIMEOUT = 10 * 60
    CATEGORIES = ["all", "accepted", "sended", "received"]

    def _invalidate_search_caches(self, user1_id, user2_id):
        # Сбрасываем и общий список друзей:
        for uid in (user1_id, user2_id):
            for cat in self.CATEGORIES:
                cache.delete(f"friend_list_{uid}_{cat}")
        # И сбрасываем кэши поиска:
        cache.delete(f"user_interest_ids_{user1_id}")
        cache.delete(f"user_interest_ids_{user2_id}")
        cache.delete(f"user_hobby_ids_{user1_id}")
        cache.delete(f"user_hobby_ids_{user2_id}")
        cache.delete(f"user_music_ids_{user1_id}")
        cache.delete(f"user_music_ids_{user2_id}")

    def list(self, request):
        """
        Retrieve a list of friendship records for the authenticated user.

        Supports filtering by friendship status using the query parameter 'cat':
          - "accepted": Friendships with status "accepted".
          - "sended": Outgoing friendship requests (status "sended") sent by the user.
          - "received": Incoming friendship requests (status "sended") received by the user.

        Args:
            request (Request): The HTTP request object, which includes query parameters.

        Returns:
            Response: A DRF Response containing the serialized list of friendship records.
        """

        user = request.user
        cat = request.query_params.get("cat") or "all"
        if cat not in self.CATEGORIES:
            cat = "all"

        cache_key = f"friend_list_{user.id}_{cat}"
        data = cache.get(cache_key)
        if data is None:
            qs = Friendship.objects.filter(Q(from_user=user) | Q(to_user=user))
            if cat == "accepted":
                qs = qs.filter(status="accepted")
            elif cat == "sended":
                qs = qs.filter(from_user=user, status="sended")
            elif cat == "received":
                qs = qs.filter(to_user=user, status="sended")
            # cat == "all" оставляем всё

            data = FriendshipReadSerializer(
                qs, many=True, context={"request": request}
            ).data
            cache.set(cache_key, data, self.CACHE_TIMEOUT)

        return Response(data)

    def create(self, request):
        """
        Create a new friendship request.

        The request body must include the 'to_user' field (the ID of the user to whom the request is sent).
        A new friendship record is created with:
          - from_user: the authenticated user.
          - to_user: the user ID provided in the request.
          - status: set to "sended".

        Args:
            request (Request): The HTTP request object containing the 'to_user' in its data.

        Returns:
            Response: A DRF Response with the serialized friendship data if created successfully,
                      or error details if validation fails.
        """

        data = {
            "from_user": request.user.id,
            "to_user": request.data.get("to_user"),
            "status": "sended",
        }
        serializer = FriendshipWriteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # вернём новый объект в «read» формате
            read_ser = FriendshipReadSerializer(
                serializer.instance, context={"request": request}
            )

            user1 = request.user.id
            user2 = request.data.get("to_user")
            self._invalidate_search_caches(user1, user2)
            return Response(read_ser.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request):
        """
        Update a friendship request to accept it.

        This method processes a PATCH/PUT request where the client sends the 'other_user_id'
        (the ID of the user who originally sent the request). It finds the friendship record
        where:
          - from_user is the other user,
          - to_user is the authenticated user,
          - status is "sended".
        If found, the status is updated to "accepted".

        Args:
            request (Request): The HTTP request object containing 'other_user_id' and the new status.

        Returns:
            Response: A DRF Response containing the updated friendship data if successful,
                      or error details if the record is not found or access is denied.
        """

        other_id = request.data.get("other_user_id")
        if not other_id:
            return Response(
                {"detail": "Не указан other_user_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            fs = Friendship.objects.get(
                from_user_id=other_id, to_user=request.user, status="sended"
            )
        except Friendship.DoesNotExist:
            return Response({"detail": "Не найдено"}, status=status.HTTP_404_NOT_FOUND)

        fs.status = "accepted"
        fs.save()
        read_ser = FriendshipReadSerializer(fs, context={"request": request})

        self._invalidate_search_caches(request.user.id, other_id)
        return Response(read_ser.data)

    def destroy(self, request):
        """
        Delete a friendship record.

        The request should include the 'other_user_id' in the body, representing the ID of the other user
        in the friendship. The record is searched using a condition that checks for either:
          - from_user equals the authenticated user and to_user equals other_user_id, or
          - from_user equals other_user_id and to_user equals the authenticated user.
        If found, the record is deleted.

        Args:
            request (Request): The HTTP request object containing 'other_user_id'.

        Returns:
            Response: A DRF Response with HTTP 204 NO CONTENT if deletion is successful,
                      or error details if the record is not found or access is denied.
        """

        other_id = request.data.get("other_user_id")
        if not other_id:
            return Response(
                {"detail": "Не указан other_user_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            fs = Friendship.objects.get(
                Q(from_user=request.user, to_user_id=other_id)
                | Q(from_user_id=other_id, to_user=request.user)
            )
        except Friendship.DoesNotExist:
            return Response({"detail": "Не найдено"}, status=status.HTTP_404_NOT_FOUND)

        fs.delete()

        try:
            chat = Chats.objects.get(
                Q(user1=request.user, user2_id=other_id)
                | Q(user1_id=other_id, user2=request.user)
            )
            chat.delete()
        except Chats.DoesNotExist:
            pass

        self._invalidate_search_caches(request.user.id, other_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
