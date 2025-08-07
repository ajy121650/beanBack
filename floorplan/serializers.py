from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import FloorPlan


class FloorPlanSerializer(ModelSerializer):
    #TODO 준영
    class Meta:
        model = FloorPlan
        fields = "__all__"

class DetectionSerializer(serializers.Serializer):
    class_field = serializers.CharField(source="class")  # 'class'는 파이썬 예약어라 내부 필드명은 다르게
    confidence = serializers.FloatField()
    x = serializers.FloatField()
    y = serializers.FloatField()
    width = serializers.FloatField()
    height = serializers.FloatField()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # 'class_field'을 다시 'class'라는 이름으로 출력
        rep["class"] = rep.pop("class_field")
        return rep
    
class ImageSizeSerializer(serializers.Serializer):
    width = serializers.FloatField()
    height = serializers.FloatField()

class FloorPlanDetectionSerializer(serializers.Serializer):
    image_size = ImageSizeSerializer()
    detections = DetectionSerializer(many=True)