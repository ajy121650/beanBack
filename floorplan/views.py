from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import FloorPlan

from cafe.models import Cafe
from .serializers import FloorPlanSerializer, FloorPlanDetectionSerializer, FloorPlanRequestSerializer
from owner.models import Owner

from inference_sdk import InferenceHTTPClient
from rest_framework.parsers import MultiPartParser, FormParser
import json, cv2, tempfile

# Create your views here.

class FloorPlanListView(APIView):
    def get(self, request):
        floor_plans = FloorPlan.objects.prefetch_related("chairs", "tables").all()
        serializer = FloorPlanSerializer(floor_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        width = request.data.get("width")
        height = request.data.get("height")
        cafe_id = request.data.get("cafe_id")

        cafe = Cafe.objects.get(id=cafe_id)
        if not cafe:
            return Response({"error": "Cafe not found"}, status=status.HTTP_404_NOT_FOUND)
        floor_plan = FloorPlan.objects.create(
            width=width,
            height=height,
            cafe=cafe
        )

        serializer = FloorPlanSerializer(floor_plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FloorPlanDetailView(APIView):
    def get(self, request, floorplan_id):
        try:
                floor_plan = FloorPlan.objects.get(id=floorplan_id)
        except:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FloorPlanSerializer(floor_plan)
        return Response(serializer.data, status=status.HTTP_200_OK)
                
    def put(self, request, floorplan_id):
        floorplan = FloorPlan.objects.get(pk=floorplan_id)
        serializer = FloorPlanRequestSerializer(floorplan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self, request, floorplan_id):
        try:
            floor_plan = FloorPlan.objects.get(pk=floorplan_id)
            floor_plan.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FloorPlan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FloorPlanOwnerView(APIView):
    def get(self, request, owner_id):
        try: 
            owner = Owner.objects.get(id=owner_id)
            cafes = Cafe.objects.filter(owner=owner_id)
            cafes_id = cafes.values_list('id', flat=True)
            floor_plans = FloorPlan.objects.filter(cafe__in=cafes_id)
        except:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FloorPlanSerializer(floor_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FloorPlanCafeView(APIView):
    def get(self, request, cafe_id):
        try:
            cafe = Cafe.objects.get(id=cafe_id)
        except Cafe.DoesNotExist:
            return Response({"error": "Cafe not found"}, status=status.HTTP_404_NOT_FOUND)

        floor_plans = FloorPlan.objects.filter(cafe=cafe).prefetch_related("chairs", "tables")
        serializer = FloorPlanSerializer(floor_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FloorPlanDetectionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        image = request.FILES.get('image')
        if not image:
            return Response({"error": "No image uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
            for chunk in image.chunks():
                temp_image.write(chunk)
            temp_image_path = temp_image.name

        client = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key="WMgJWPbuVlyxzmjDsndL"
        )

        result = client.run_workflow(
            workspace_name="cho-voxnn",
            workflow_id="detect-count-and-visualize",
            images={"image": open(temp_image_path, "rb")},
            use_cache=False
        )

        first = result[0]
        detections = first["predictions"]["predictions"]
        width = first["image"]["width"]
        height = first["image"]["height"]

        response_data = {
            "image_size": {
                "width": width,
                "height": height
            },
            "detections": [
                {
                    "class": det["class"],
                    "confidence": det["confidence"],
                    "x": det["x"],
                    "y": det["y"],
                    "width": det["width"],
                    "height": det["height"]
                }
                for det in detections
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)

