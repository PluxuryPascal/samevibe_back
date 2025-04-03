from django.db import models
from django.contrib.auth.models import User

class Friendship(models.Model):
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_request", db_index=True
    )
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_request", db_index=True
    )
    status = models.CharField(max_length=20, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("from_user", "to_user"),)
        indexes = [
            models.Index(fields=["from_user", "to_user"]),
            models.Index(fields=["status"]),
        ]