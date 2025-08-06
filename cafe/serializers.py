from rest_framework import serializers
from .models import Cafe, CafeTagRating
from tag.serializers import TagSerializer

class CafeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    keywords = TagSerializer(many=True, read_only=True)
    class Meta:
        model = Cafe
        fields = '__all__'

# read_only
class CafeTagRatingSerializer(serializers.ModelSerializer):
    cafe = CafeSerializer(read_only=True)
    tag = TagSerializer(read_only=True)
    class Meta:
        model = CafeTagRating
        fields = ['id', 'cafe', 'tag', 'rating']

# write_only
class CafeTagRatingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeTagRating
        fields = ['cafe', 'tag', 'rating']