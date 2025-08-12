from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import FloorPlan
from cafe.models import Cafe
from .serializers import FloorPlanSerializer, FloorPlanDetectionSerializer, FloorPlanRequestSerializer

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
        #TODO 수현
        #pass 키워드 지우고 구현하기
        pass

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
        #TODO 수현
        #pass 키워드 지우고 구현하기
        pass

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
    def get(self, request):
        #TODO 민경
        #pass 키워드 지우고 구현하기
        pass