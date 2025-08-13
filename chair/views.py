from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Chair
from .serializers import ChairSerializer, ChairRequestSerializer

class ChairListView(APIView):
    def get(self, request):
        #TODO 일단 미개발 필요없을 가능성 농후
        # pass 키워드 지우고 구현하기
        pass

    def post(self, request):
        #TODO 일단 미개발 필요없을 가능성 농후
        # pass 키워드 지우고 구현하기
        pass
    

class ChairDetailView(APIView):
    def get(self, request, chair_id):
        #TODO 일단 미개발 필요없을 가능성 농후
        # pass 키워드 지우고 구현하기
        pass

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
        
    def delete(self, request, chair_id):
        try:
            chair = Chair.objects.get(pk=chair_id)
            chair.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Chair.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        