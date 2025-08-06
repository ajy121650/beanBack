from rest_framework import serializers
from .models import Review
from tag.serializers import TagSerializer

class ReviewSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = Review
        fields = '__all__'