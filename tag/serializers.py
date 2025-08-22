from rest_framework.serializers import ModelSerializer
from .models import Tag

# 태그 정보 시리얼라이저
class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
