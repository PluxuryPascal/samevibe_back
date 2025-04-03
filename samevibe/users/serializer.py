from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Profile

from interests.models import UserInterest, UserHobby, UserMusic
from friends.models import Friendship


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
        )


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = (
            "user",
            "photo",
            "gender",
        )

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            user_serializer = self.fields["user"]
            user_serializer.update(instance.user, user_data)
        instance.photo = validated_data.get("photo", instance.photo)
        instance.gender = validated_data.get("gender", instance.gender)
        instance.save()
        return instance


class InterestMatchedUserSerializer(serializers.ModelSerializer):
    percentage = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "gender",
            "percentage",
            "status",
        )

    def get_percentage(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0

        current_user = request.user
        current_interests = set(
            current_user.userinterest_set.values_list("interest__id", flat=True)
        )
        other_interests = set(
            obj.userinterest_set.values_list("interest__id", flat=True)
        )

        if not current_interests:
            return 0

        common = current_interests.intersection(other_interests)

        return round((len(common) / len(current_interests)) * 100)

    def get_status(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0

        current_user = request.user
        friendship = Friendship.objects.filter(
            Q(from_user=current_user, to_user=obj)
            | Q(from_user=obj, to_user=current_user)
        ).first()

        if friendship:
            return friendship.status
        return None

    def get_gender(self, obj):
        try:
            return obj.profile.gender
        except Profile.DoesNotExist:
            return None


class HobbyMatchedUserSerializer(serializers.ModelSerializer):
    percentage = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "gender",
            "percentage",
            "status",
        )

    def get_percentage(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0

        current_user = request.user
        current_hobbies = set(
            current_user.userhobby_set.values_list("hobby__id", flat=True)
        )
        other_hobbies = set(obj.userhobby_set.values_list("hobby__id", flat=True))

        if not current_hobbies:
            return 0

        common = current_hobbies.intersection(other_hobbies)

        return round((len(common) / len(current_hobbies)) * 100)

    def get_status(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0

        current_user = request.user
        friendship = Friendship.objects.filter(
            Q(from_user=current_user, to_user=obj)
            | Q(from_user=obj, to_user=current_user)
        ).first()

        if friendship:
            return friendship.status
        return None

    def get_gender(self, obj):
        try:
            return obj.profile.gender
        except Profile.DoesNotExist:
            return None


class MusicMatchedUserSerializer(serializers.ModelSerializer):
    percentage = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "gender",
            "percentage",
            "status",
        )

    def get_percentage(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0

        current_user = request.user
        current_genre = set(
            current_user.usermusic_set.values_list("genre__id", flat=True)
        )
        other_genre = set(obj.usermusic_set.values_list("genre__id", flat=True))

        if not current_genre:
            return 0

        common = current_genre.intersection(other_genre)

        return round((len(common) / len(current_genre)) * 100)

    def get_status(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0

        current_user = request.user
        friendship = Friendship.objects.filter(
            Q(from_user=current_user, to_user=obj)
            | Q(from_user=obj, to_user=current_user)
        ).first()

        if friendship:
            return friendship.status
        return None

    def get_gender(self, obj):
        try:
            return obj.profile.gender
        except Profile.DoesNotExist:
            return None
