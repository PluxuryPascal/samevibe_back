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
    last_message = serializers.SerializerMethodField()
    last_time = serializers.SerializerMethodField()
    last_message_sender_id = serializers.SerializerMethodField()

    class Meta:
        model = Chats
        fields = (
            "id",
            "user1",
            "user2",
            "created_at",
            "updated_at",
            "other_user",
            "last_message",
            "last_time",
            "last_message_sender_id",
        )

    def get_other_user(self, instance):
        me = self.context["request"].user
        other = instance.user2 if instance.user1 == me else instance.user1
        return UserInfoSerializer(other).data

    def get_last_message(self, instance):
        msg = instance.contents_set.order_by("-created_at").first()
        return msg.text if msg else ""

    def get_last_time(self, instance):
        msg = instance.contents_set.order_by("-created_at").first()
        return msg.created_at.isoformat() if msg else None

    def get_last_message_sender_id(self, instance):
        msg = instance.contents_set.order_by("-created_at").first()
        return msg.sender.id if msg else None


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
