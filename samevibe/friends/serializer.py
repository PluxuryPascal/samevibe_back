from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Friendship
from users.models import Profile


class FriendInfoSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    avatar = serializers.ImageField(source="user.profile.photo", allow_null=True)

    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "avatar")


class FriendshipReadSerializer(serializers.ModelSerializer):
    other = serializers.SerializerMethodField()
    other_id = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ("status", "other_id", "other")

    def get_other(self, instance):
        req_user = self.context["request"].user
        other_user = (
            instance.to_user if instance.from_user == req_user else instance.from_user
        )
        profile = other_user.profile
        return {
            "first_name": other_user.first_name,
            "last_name": other_user.last_name,
            "avatar": profile.photo if profile.photo else None,
        }

    def get_other_id(self, instance):
        req_user = self.context["request"].user
        return (
            instance.to_user.id
            if instance.from_user == req_user
            else instance.from_user.id
        )


class FriendshipWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ("from_user", "to_user", "status")
