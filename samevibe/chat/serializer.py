from rest_framework import serializers
from .models import Chats, Contents
from django.contrib.auth.models import User


class ChatSerializer(serializers.ModelSerializer):
    user1 = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user2 = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Chats
        fields = ("id", "user1", "user2", "created_at", "updated_at")


class ContentSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    chat = serializers.PrimaryKeyRelatedField(queryset=Chats.objects.all())

    class Meta:
        model = Contents
        fields = (
            "id",
            "text",
            "attachment",
            "sender",
            "chat",
            "created_at",
            "updated_at",
        )
