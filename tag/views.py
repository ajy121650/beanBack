from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Tag
from .serializers import TagSerializer

from cafe.models import Cafe, CafeTagRating
from cafe.serializers import CafeTagRatingSerializer, CafeTagRatingCreateSerializer
from drf_yasg.utils import swagger_auto_schema


class TagListView(APIView):
  @swagger_auto_schema(
    operation_id='태그 목록 조회',
    operation_description='태그 목록을 조회합니다.',
    responses={200: TagSerializer(many=True)}
  )
  def get(self, request):
    tags = Tag.objects.all()
    serializer = TagSerializer(instance=tags, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

  @swagger_auto_schema(
    operation_id='태그 생성',
    operation_description='태그를 생성합니다.',
    request_body=TagSerializer,
    responses={201: TagSerializer}
  )
  def post(self, request):
    content = request.data.get('content')
    
    if not content:
      return Response({"detail": "missing fields ['content']"}, status=status.HTTP_400_BAD_REQUEST)

    if Tag.objects.filter(content=content).exists():
      return Response({"detail" : "Tag with same content already exists"}, status=status.HTTP_409_CONFLICT)

    tag = Tag.objects.create(content=content)
    serializer = TagSerializer(instance = tag)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class CafeTagRatingView(APIView):
  
  @swagger_auto_schema(
    operation_id='태그에 해당하는 카페와 별점 조회',
    operation_description='해당 태그에 대한 카페와 별점을 별점순으로 조회합니다.',
    responses={200: CafeTagRatingSerializer(many=True), 204: 'No Content'}
  )
  def get(self, request, tag_id):
    try:
      Tag.objects.get(id=tag_id)
    except:
      return Response({"detail": "Provided tag does not exist."}, status=status.HTTP_204_NO_CONTENT)
    
    ratings = CafeTagRating.objects.filter(tag_id=tag_id).order_by('-rating') 
    serializer = CafeTagRatingSerializer(instance=ratings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  @swagger_auto_schema(
    operation_id='카페와 태그에 따른 별점 생성',
    operation_description='카페와 태그에 따른 별점을 생성합니다.',
    request_body=CafeTagRatingSerializer,
    responses={201: CafeTagRatingSerializer}
  )
  def post(self, request):
    serializer = CafeTagRatingCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Check if Cafe and Tag exist
        cafe_id = serializer.validated_data['cafe'].id
        tag_id = serializer.validated_data['tag'].id
        if not Cafe.objects.filter(id=cafe_id).exists():
            return Response({"detail": "Cafe not found."}, status=status.HTTP_400_BAD_REQUEST)
        if not Tag.objects.filter(id=tag_id).exists():
            return Response({"detail": "Tag not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Save and respond
        rating_instance = serializer.save()
        full_serializer = CafeTagRatingSerializer(rating_instance)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CafeTagRatingDetailView(APIView):
    
  def get_object(self, rating_id):
    try:
      return CafeTagRating.objects.get(id=rating_id)
    except CafeTagRating.DoesNotExist:
      return None

  @swagger_auto_schema(
      operation_id='별점 수정',
      operation_description='특정 CafeTagRating의 별점을 수정합니다.',
      request_body=CafeTagRatingCreateSerializer,
      responses={200: CafeTagRatingSerializer, 404: 'Not Found'}
  )
  def put(self, request, rating_id):
      instance = self.get_object(rating_id)
      if not instance:
          return Response({"detail": "Rating not found."}, status=status.HTTP_404_NOT_FOUND)

      serializer = CafeTagRatingCreateSerializer(instance, data=request.data)
      if serializer.is_valid():
          updated = serializer.save()
          return Response(CafeTagRatingSerializer(updated).data, status=status.HTTP_200_OK)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  @swagger_auto_schema(
      operation_id='별점 삭제',
      operation_description='특정 CafeTagRating을 삭제합니다.',
      responses={204: 'No Content', 404: 'Not Found'}
  )
  def delete(self, request, rating_id):
      instance = self.get_object(rating_id)
      if not instance:
          return Response({"detail": "Rating not found."}, status=status.HTTP_404_NOT_FOUND)

      instance.delete()
      return Response(status=status.HTTP_204_NO_CONTENT)