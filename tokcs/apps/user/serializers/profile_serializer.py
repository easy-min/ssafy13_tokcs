from rest_framework import serializers
from ..models.profile import UserProfile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "nickname",
            "total_score",
            "level",
            "tier",
            "created_at",
            "last_active",
        ]
        read_only_fields = ["total_score", "level", "tier", "created_at", "last_active"]
