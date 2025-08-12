from django.shortcuts import render

# Create your views here.
# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Owner
from cafe.models import Cafe
from cafe.serializers import CafeSerializer

class OwnerDetailCafeListView(APIView):
    def get(self, request, owner_id):
        try:
            owner = Owner.objects.get(id=owner_id)
        except Owner.DoesNotExist:
            return Response({"error": "Owner not found"}, status=status.HTTP_404_NOT_FOUND)

        cafes = Cafe.objects.filter(owner=owner)
        serializer = CafeSerializer(cafes, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    