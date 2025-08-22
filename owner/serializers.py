from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import Owner

# User ID와 Username만 포함하는 Serializer
class UserIdUsernameSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]

# 유저 정보 시리얼라이저
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]

# 점주 정보 시리얼라이저
class OwnerSerializer(ModelSerializer):
    owner = UserSerializer(read_only=True)
    class Meta:
        model = Owner
        fields = ["id", "owner"]