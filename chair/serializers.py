from rest_framework.serializers import ModelSerializer
from .models import Chair

class ChairSerializer(ModelSerializer):
    class Meta:
        model = Chair
        fields = "__all__"

class ChairRequestSerializer(ModelSerializer):
    class Meta:
        model = Chair
        fields = ['width', 'height', 'x_position', 'y_position', 'socket', 'window', 'occupied', 'floor_plan']