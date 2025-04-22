# tokcs/apps/user/views/signup_view.py

from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from ..serializers.signup_serializer import SignupSerializer

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]
