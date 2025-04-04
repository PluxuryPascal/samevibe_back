from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.URLField(blank=True)
    gender = models.BooleanField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=["gender"]),
        ]

    # birth_date = models.DateField(null=True, blank=True)
