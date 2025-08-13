from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import Owner


class UserIdUsernameSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]


class OwnerSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Owner
        fields = "__all__"