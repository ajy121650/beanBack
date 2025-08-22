from rest_framework.serializers import ModelSerializer
from .models import Table

# 테이블 정보 시리얼라이저
class TableSerializer(ModelSerializer):
    class Meta:
        model = Table
        fields = "__all__"