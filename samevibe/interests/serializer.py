from rest_framework import serializers

from .models import Interest, Hobby, MusicGenre, UserInterest, UserHobby, UserMusic


class InterestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interest
        fields = (
            "id",
            "name",
        )


class HobbySerializer(serializers.ModelSerializer):

    class Meta:
        model = Hobby
        fields = (
            "id",
            "name",
        )


class MusicGenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = MusicGenre
        fields = (
            "id",
            "name",
        )


class UserInterestSerializer(serializers.ModelSerializer):

    interest_id = serializers.PrimaryKeyRelatedField(
        queryset=Interest.objects.all(), source="interest"
    )

    class Meta:
        model = UserInterest
        fields = ("interest_id",)

    def create(self, validated_data):
        user = self.context["request"].user
        return UserInterest.objects.create(user=user, **validated_data)


class UserHobbiesSerializer(serializers.ModelSerializer):

    hobby_id = serializers.PrimaryKeyRelatedField(
        queryset=Hobby.objects.all(), source="hobby"
    )

    class Meta:
        model = UserHobby
        fields = ("hobby_id",)

    def create(self, validated_data):
        user = self.context["request"].user
        return UserHobby.objects.create(user=user, **validated_data)


class UserMusicSerializer(serializers.ModelSerializer):

    music_id = serializers.PrimaryKeyRelatedField(
        queryset=MusicGenre.objects.all(), source="genre"
    )

    class Meta:
        model = UserMusic
        fields = ("music_id",)

    def create(self, validated_data):
        user = self.context["request"].user
        return UserMusic.objects.create(user=user, **validated_data)
