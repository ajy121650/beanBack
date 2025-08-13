from django.shortcuts import render

# Create your views here.
# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Table
from .serializers import TableSerializer

class TableListView(APIView):
    def get(self, request):
        tables = Table.objects.all()
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class TableDetailView(APIView):
    def get(self, request, table_id):
        try:
            table = Table.objects.get(id=table_id)
            serializer = TableSerializer(table)
            return Response(serializer.data)
        except Table.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
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