from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Friendship
from .serializer import FriendshipSerializer


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
        queryset = Friendship.objects.filter(Q(from_user=user) | Q(to_user=user))
        cat = request.query_params.get("cat")

        if cat == "accepted":
            queryset = queryset.filter(status=cat)
        elif cat == "sended":
            queryset = queryset.filter(from_user=user, status=cat)
        elif cat == "received":
            queryset = queryset.filter(to_user=user, status="sended")

        serializer = FriendshipSerializer(queryset, many=True)

        return Response(serializer.data)

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

        to_user_id = request.data.get("to_user")
        if not to_user_id:
            return Response(
                {"detail": "Необходимо указать получателя заявки."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = {"from_user": request.user.id, "to_user": to_user_id, "status": "sended"}

        serializer = FriendshipSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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

        other_user_id = request.data.get("other_user_id")
        if not other_user_id:
            return Response(
                {"detail": "Не указан идентификатор другого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user

        try:
            friendship = Friendship.objects.get(
                from_user_id=other_user_id, to_user=user, status="sended"
            )
        except Friendship.DoesNotExist:
            return Response(
                {"detail": "Запись не найдена или нет доступа для принятия заявки."},
                status=status.HTTP_404_NOT_FOUND,
            )

        friendship.status = "accepted"
        friendship.save()

        serializer = FriendshipSerializer(friendship)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

        other_user_id = request.data.get("other_user_id")
        if not other_user_id:
            return Response(
                {"detail": "Не указан идентификатор другого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user

        try:
            friendship = Friendship.objects.get(
                Q(from_user=user, to_user_id=other_user_id)
                | Q(from_user_id=other_user_id, to_user=user)
            )
        except Friendship.DoesNotExist:
            return Response(
                {"detail": "Запись не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        friendship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
