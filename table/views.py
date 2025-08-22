from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Table
from .serializers import TableSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class TableListView(APIView):
    @swagger_auto_schema(
        operation_id="테이블 목록 조회",
        operation_description="모든 테이블의 목록을 반환합니다.",
        responses={200: TableSerializer(many=True)}
    )
    def get(self, request):
        tables = Table.objects.all()
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_id="테이블 생성",
        operation_description="새로운 테이블을 생성합니다.",
        request_body=TableSerializer,
        responses={201: TableSerializer, 400: "Bad Request"}
    )
    def post(self, request):
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class TableDetailView(APIView):
    @swagger_auto_schema(
        operation_id="테이블 상세 조회",
        operation_description="table_id에 해당하는 테이블의 상세 정보를 반환합니다.",
        manual_parameters=[
            openapi.Parameter(
                'table_id',
                openapi.IN_PATH,
                description="테이블 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: TableSerializer, 404: "Not found"}
    )
    def get(self, request, table_id):
        try:
            table = Table.objects.get(id=table_id)
            serializer = TableSerializer(table)
            return Response(serializer.data)
        except Table.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_id="테이블 수정",
        operation_description="table_id에 해당하는 테이블을 수정합니다.",
        request_body=TableSerializer,
        responses={200: TableSerializer, 404: "Not found"}
    )
    def put(self, request, table_id):
        try:
            table = Table.objects.get(id=table_id)
            serializer = TableSerializer(table, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Table.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)