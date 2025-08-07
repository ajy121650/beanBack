from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import FloorPlan
from .serializers import FloorPlanSerializer, FloorPlanDetectionSerializer

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
        #TODO 
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
        #TODO 민경
        #pass 키워드 지우고 구현하기
        pass