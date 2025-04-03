from django.db import models
from django.contrib.auth.models import User



class Chats(models.Model):
    user1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages", db_index=True
    )
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages", db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("user1", "user2"),)
        indexes = [
            models.Index(fields=["user1", "user2"]),
            models.Index(fields=["created_at"]),
        ]

class Contents(models.Model):
    text = models.TextField()
    attachment = models.URLField(blank=True, null=True)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True
    )
    chat = models.ForeignKey(
        Chats, on_delete=models.CASCADE, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["chat", "created_at"]),
            models.Index(fields=["sender"]),
        ]
