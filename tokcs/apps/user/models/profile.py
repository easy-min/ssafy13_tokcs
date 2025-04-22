from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    nickname = models.CharField(max_length=100, unique=True)
    total_score = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    tier = models.PositiveIntegerField(default="Bronze")
    created_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nickname} ({self.tier})"