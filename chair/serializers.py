from rest_framework.serializers import ModelSerializer
from .models import Chair

class ChairSerializer(ModelSerializer):
    class Meta:
        model = Chair
        fields = "__all__"