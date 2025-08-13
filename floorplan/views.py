from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import FloorPlan
from .serializers import FloorPlanSerializer, FloorPlanDetectionSerializer

from inference_sdk import InferenceHTTPClient
import json, cv2

class FloorPlanListView(APIView):
    def get(self, request):
        floor_plans = FloorPlan.objects.all()
        serializer = FloorPlanSerializer(floor_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        #TODO 준영
        #pass 키워드 지우고 구현하기
        pass


class FloorPlanDetailView(APIView):
    def get(self, request, floorplan_id):
        #TODO 수현
        #pass 키워드 지우고 구현하기
        pass

    def put(self, request, floorplan_id):
        #TODO 준영
        #pass 키워드 지우고 구현하기
        pass
        

    def delete(self, request, floorplan_id):
        try:
            floor_plan = FloorPlan.objects.get(pk=floorplan_id)
            floor_plan.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FloorPlan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FloorPlanOwnerView(APIView):
    def get(self, request, owner_id):
        #TODO 수현
        #pass 키워드 지우고 구현하기
        pass
    
class FloorPlanDetectionView(APIView):
    def get(self, request):
        image_url = request.query_params.get("image_url")
        if not image_url:
            return Response({"error": "image_url query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        client = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key="WMgJWPbuVlyxzmjDsndL"
        )

        result = client.run_workflow(
            workspace_name="cho-voxnn",
            workflow_id="detect-count-and-visualize",
            images={"image": image_url},
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