from rest_framework import serializers
from .models import Chats, Contents
from django.contrib.auth.models import User
from users.models import Profile


class UserInfoSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source="profile.photo", allow_null=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "avatar")


class ChatSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()

    class Meta:
        model = Chats
        fields = ("id", "user1", "user2", "created_at", "updated_at", "other_user")

    def get_other_user(self, instance):
        me = self.context["request"].user
        other = instance.user2 if instance.user1 == me else instance.user1
        return UserInfoSerializer(other).data


class ContentSerializer(serializers.ModelSerializer):
    sender_info = serializers.SerializerMethodField()

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
            "sender_info",
        )

    def get_sender_info(self, instance):
        return UserInfoSerializer(instance.sender).data
