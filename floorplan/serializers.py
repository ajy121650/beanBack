from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import FloorPlan
from chair.serializers import ChairSerializer
from table.serializers import TableSerializer

# 생성된 카페 도면 정보 시리얼라이저
class FloorPlanSerializer(ModelSerializer):
    chairs = ChairSerializer(many=True, read_only=True)
    tables = TableSerializer(many=True, read_only=True)

    class Meta:
        model = FloorPlan
        fields = "__all__"

# 카페 도면 request 시리얼라이저
class FloorPlanRequestSerializer(ModelSerializer):
    class Meta:
        model = FloorPlan
        fields = ["width", "height", "cafe"]

# 카페 도면 요소 검출 결과 시리얼라이저 : 삽입한 사진에서 추출한 도면 요소 정보
class DetectionSerializer(serializers.Serializer):
    class_field = serializers.CharField(source="class") 
    confidence = serializers.FloatField()
    x = serializers.FloatField()
    y = serializers.FloatField()
    width = serializers.FloatField()
    height = serializers.FloatField()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["class"] = rep.pop("class_field")
        return rep

# 카페 도면 이미지 크기 정보 시리얼라이저 : 
class ImageSizeSerializer(serializers.Serializer):
    width = serializers.FloatField()
    height = serializers.FloatField()

# 생성된 최종 카페 도면 정보 시리얼라이저 (DetectionSerializer + ImageSizeSerializer)
class FloorPlanDetectionSerializer(serializers.Serializer):
    image_size = ImageSizeSerializer()
    detections = DetectionSerializer(many=True)