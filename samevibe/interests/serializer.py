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

    interest = InterestSerializer()

    class Meta:
        model = UserInterest
        fields = ("interest",)

    def create(self, validated_data):
        user = self.context["request"].user
        return UserInterest.objects.create(user=user, **validated_data)


class UserHobbiesSerializer(serializers.ModelSerializer):

    hobby = HobbySerializer()

    class Meta:
        model = UserHobby
        fields = ("hobby",)

    def create(self, validated_data):
        user = self.context["request"].user
        return UserHobby.objects.create(user=user, **validated_data)


class UserMusicSerializer(serializers.ModelSerializer):

    genre = MusicGenreSerializer()

    class Meta:
        model = UserMusic
        fields = ("genre",)

    def create(self, validated_data):
        user = self.context["request"].user
        return UserMusic.objects.create(user=user, **validated_data)
