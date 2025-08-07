from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Chair

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
        #TODO 수현
        # pass 키워드 지우고 구현하기
        pass

    def delete(self, request, chair_id):
        try:
            chair = Chair.objects.get(pk=chair_id)
            chair.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Chair.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)