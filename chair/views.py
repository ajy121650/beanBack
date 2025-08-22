from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Chair, FloorPlan
from .serializers import ChairSerializer, ChairRequestSerializer

# 카페 도면 의자 목록 전체 조회 및 생성 API 
class ChairListView(APIView):
    @swagger_auto_schema(
        operation_id="의자 목록 조회",
        operation_description="모든 의자의 목록을 조회합니다.",
        responses={200: ChairSerializer(many=True)}
    )
    def get(self, request):
        chairs = Chair.objects.all()
        serializer = ChairSerializer(chairs, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_id="의자 생성",
        operation_description="새로운 의자를 생성합니다.",
        request_body=ChairSerializer,
        responses={201: ChairSerializer, 400: "Bad Request"},
    )
    def post(self, request):
        serializer = ChairSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# 카페 도면 의자 개별 상세 조회, 수정, 삭제 API
class ChairDetailView(APIView):
    @swagger_auto_schema(
        operation_id="의자 정보 조회",
        operation_description="chair_id에 해당하는 의자 정보를 조회합니다.",
        responses={200: ChairSerializer, 404: "Not found"},
        manual_parameters=[
            openapi.Parameter(
                'chair_id',
                openapi.IN_PATH,
                description="의자 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    def get(self, request, chair_id):
        try:
            chair = Chair.objects.get(pk=chair_id)
            serializer = ChairSerializer(chair)
            return Response(serializer.data)
        except Chair.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_id="의자 정보 수정",
        operation_description="chair_id에 해당하는 의자 정보를 수정합니다.",
        request_body=ChairRequestSerializer,
        responses={200: ChairSerializer, 400: "Bad Request", 404: "Not found"},
        manual_parameters=[
            openapi.Parameter(
                'chair_id',
                openapi.IN_PATH,
                description="의자 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    def put(self, request, chair_id):
        try:
            chair = Chair.objects.get(pk=chair_id)
            serializer = ChairRequestSerializer(chair, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Chair.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(
        operation_id="의자 삭제",
        operation_description="chair_id에 해당하는 의자를 삭제합니다.",
        responses={204: "No Content", 404: "Not found"},
        manual_parameters=[
            openapi.Parameter(
                'chair_id',
                openapi.IN_PATH,
                description="의자 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    def delete(self, request, chair_id):
        try:
            chair = Chair.objects.get(pk=chair_id)
            chair.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Chair.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
