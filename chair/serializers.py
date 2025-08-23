from rest_framework.serializers import ModelSerializer
from .models import Chair

# 카페 도면 의자 정보 시리얼라이저
class ChairSerializer(ModelSerializer):
    class Meta:
        model = Chair
        fields = "__all__"

# 카페 도면 의자 생성/수정 정보 시리얼라이저
class ChairRequestSerializer(ModelSerializer):
    class Meta:
        model = Chair
        fields = ['width', 'height', 'x_position', 'y_position', 'socket', 'window', 'occupied', 'floor_plan', 'entry_time']
