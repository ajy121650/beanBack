from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Cafe, CafeTagRating
from .serializers import CafeSerializer
from tag.models import Tag
from .utils.in_memory_faiss import search_with_address_and_keywords_then_embedding
import traceback
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from owner.models import Owner

# 전체 카페 목록 조회 및 카페 생성 API
class CafeListView(APIView):
    @swagger_auto_schema(
        operation_id="카페 목록 조회",
        operation_description="모든 카페의 목록을 반환합니다.",
        responses={200: CafeSerializer(many=True)}
    )
    def get(self, request):
        cafes =Cafe.objects.all()
        serializer = CafeSerializer(cafes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_id="카페 생성",
        operation_description="새로운 카페를 생성합니다.",
        request_body=CafeSerializer,
        responses={201: CafeSerializer, 404: "Not Found", 400: "Bad Request", 401: "Unauthorized"},
        manual_parameters=[openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)]
    )
    def post(self, request):
        
        name = request.data.get("name")
        address = request.data.get("address")
        description = request.data.get("description")
        photo_urls = request.data.get("photo_urls")
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            owner = Owner.objects.get(owner=user)
        except Owner.DoesNotExist:
            owner = Owner.objects.create(owner=user)
        
        if not name:
            return Response(
                {"detail": "[name] field is missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not address:
            return Response(
                {"detail": "[address] field is missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tag_contents = request.data.get("tags")
        keyword_contents = request.data.get("keywords")

        if not description:
            description = ""
        
        if not photo_urls:
            photo_urls = []

        cafe = Cafe.objects.create(
                name=name,
                address=address,
                description=description,
                average_rating=0.0,
                photo_urls=photo_urls,
                owner=owner, 
            )

        if tag_contents is not None:
            for tag_content in tag_contents:
                tag = Tag.objects.create(content = tag_content)
                CafeTagRating.objects.create(cafe = cafe, tag = tag, rating = 0.0)

        if keyword_contents is not None:
            for keyword_content in keyword_contents:
                if not Tag.objects.filter(content = keyword_content).exists():
                    cafe.keywords.create(content = keyword_content)
                else:
                    cafe.keywords.add(Tag.objects.get(content = keyword_content))

        serializer = CafeSerializer(cafe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# 개별 카페 상세 조회, 수정, 삭제 API
class CafeDetailView(APIView):
    @swagger_auto_schema(
        operation_id="카페 상세 조회",
        operation_description="cafe_id에 해당하는 카페의 상세 정보를 반환합니다.",
        manual_parameters=[
            openapi.Parameter(
                'cafe_id',
                openapi.IN_PATH,
                description="카페 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: CafeSerializer, 404: "Not found"}
    )
    def get(self, request, cafe_id):
        try:
            cafe = Cafe.objects.get(id=cafe_id)
        except:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CafeSerializer(instance=cafe)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="카페 삭제",
        operation_description="cafe_id에 해당하는 카페를 삭제합니다.",
        responses={204: "No Content", 404: "Not found"},
        manual_parameters=[
            openapi.Parameter(
                'cafe_id',
                openapi.IN_PATH,
                description="카페 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    def delete(self, request, cafe_id):
        try:
            cafe = Cafe.objects.get(id=cafe_id)
        except:
            return Response(
                {"detail": "Cafe Not found."}, status=status.HTTP_404_NOT_FOUND
            )

        cafe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_id="카페 정보 수정",
        operation_description="cafe_id에 해당하는 카페 정보를 수정합니다.",
        request_body=CafeSerializer,
        responses={200: CafeSerializer, 400: "Bad Request", 404: "Not found"},
        manual_parameters=[
            openapi.Parameter(
                'cafe_id',
                openapi.IN_PATH,
                description="카페 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    def put(self, request, cafe_id):
        try:
            cafe = Cafe.objects.get(id=cafe_id)
        except:
            return Response(
                {"detail": "Cafe not found."}, status=status.HTTP_404_NOT_FOUND
            )

        name = request.data.get("name")
        address = request.data.get("address")
        description = request.data.get("description")
        photo_urls = request.data.get("photo_urls")
        pos_connected = request.data.get("pos_connected")
        
        if name:
            cafe.name = name
        
        if address:
            cafe.address = address
        
        if description:
            cafe.description = description
        
        if photo_urls:
            cafe.photo_urls = photo_urls
        
        if pos_connected:
            cafe.pos_connected = pos_connected

        keyword_contents = request.data.get("keywords")

        
        if keyword_contents is not None:
            cafe.keywords.clear()
            for keyword_content in keyword_contents:
                if not Tag.objects.filter(content=keyword_content).exists():
                    cafe.keywords.create(content=keyword_content)
                else:
                    cafe.keywords.add(Tag.objects.get(content=keyword_content))

        cafe.save()
        serializer = CafeSerializer(instance=cafe)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# 챗봇 검색 API
class CafeChatView(APIView):
    @swagger_auto_schema(
        operation_id="카페 질문하기",
        operation_description="카페에 대한 질문을 합니다.",
        manual_parameters=[
            openapi.Parameter(
                'question',
                openapi.IN_QUERY,
                description="질문 내용",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: "Success", 400: "Bad Request"}
    )
    def get(self, request):
        try:
            question = request.query_params.get("question")
            if not question:
                return Response(
                    {"error": "question 쿼리스트링을 넣어주세요."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if question == "test":
                cafes = Cafe.objects.filter(id__gte=14701) #시연용
            else:
                cafes = search_with_address_and_keywords_then_embedding(question, top_k=15)

        except Exception as e:
            traceback.print_exc()        
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        serializer = CafeSerializer(cafes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class CafeViewSet(viewsets.ModelViewSet):
    queryset = Cafe.objects.all().order_by('-created_at')
    serializer_class = CafeSerializer
