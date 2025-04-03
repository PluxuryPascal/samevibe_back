from django.db import models
from django.contrib.auth.models import User


class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        indexes = [models.Index(fields=["name"])]


class Hobby(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        indexes = [models.Index(fields=["name"])]


class MusicGenre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        indexes = [models.Index(fields=["name"])]


# Throw Models
class UserInterest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE, db_index=True)

    class Meta:
        unique_together = (("user", "interest"),)
        indexes = [
            models.Index(fields=["user", "interest"]),
        ]


class UserHobby(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    hobby = models.ForeignKey(Hobby, on_delete=models.CASCADE, db_index=True)

    class Meta:
        unique_together = (("user", "hobby"),)
        indexes = [
            models.Index(fields=["user", "hobby"]),
        ]


class UserMusic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    genre = models.ForeignKey(MusicGenre, on_delete=models.CASCADE, db_index=True)

    class Meta:
        unique_together = (("user", "genre"),)
        indexes = [
            models.Index(fields=["user", "genre"]),
        ]
