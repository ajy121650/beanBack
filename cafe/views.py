from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Cafe, CafeTagRating
from .serializers import CafeSerializer
from tag.models import Tag

from .utils.in_memory_faiss import search_similar_cafes
import traceback

import json
import os

class CafeListView(APIView):
    def get(self, request):
        cafes =Cafe.objects.all()
        serializer = CafeSerializer(cafes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        name = request.data.get("name")
        address = request.data.get("address")
        description = request.data.get("description")
        photo_urls = request.data.get("photo_urls")
        pos_connected = request.data.get("pos_connected")

        tag_contents = request.data.get("tags")
        keyword_contents = request.data.get("keywords")

        if not description:
            description = ""
        
        if not photo_urls:
            photo_urls = []
        
        if not pos_connected:
            pos_connected = False

        cafe = Cafe.objects.create(
                name=name,
                address=address,
                description=description,
                has_wifi=True,
                average_rating=0.0,
                photo_urls=photo_urls,
                pos_connected=pos_connected
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


class CafeDetailView(APIView):
    def get(self, request, cafe_id):
        try:
            cafe = Cafe.objects.get(id=cafe_id)
        except:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CafeSerializer(instance=cafe)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, cafe_id):
        try:
            cafe = Cafe.objects.get(id=cafe_id)
        except:
            return Response(
                {"detail": "Cafe Not found."}, status=status.HTTP_404_NOT_FOUND
            )

        cafe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

        #tag_contents = request.data.get("tags") 일단 태그 데이터는 여기서 수정 X
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
    
class CafeChatView(APIView):
    def get(self, request):
        try:
            question = request.data.get("question")
            if not question:
                return Response(
                    {"error": "question 필드를 전달해주세요."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # FAISS + RAG 검색
            cafes = search_similar_cafes(question, top_k=10)
        except Exception as e:
            traceback.print_exc()         # 터미널에 전체 에러 스택 출력
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        #직렬화
        serializer = CafeSerializer(cafes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CafeUploadView(APIView):
    def post(self, request):
        try:
            # file_path = "data/cafe_opened_data.json"  # 로컬 경로 지정 (프로젝트 기준 상대경로 또는 절대경로 사용)
            file_path = "data/cafe_opened_random.json"  # 로컬 경로 지정 (프로젝트 기준 상대경로 또는 절대경로 사용)

            if not os.path.exists(file_path):
                return Response({"detail": f"File not found: {file_path}"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                return Response({"detail": "Invalid JSON format."}, status=status.HTTP_400_BAD_REQUEST)

            created_cafes = []

            for item in data:
                name = item.get('bplcnm')
                address = item.get('rdnwhladdr')
                if not name or not address:
                    continue  # 필수 필드 없으면 무시

                cafe = Cafe.objects.create(
                    name=name,
                    address=address,
                    description="",
                    average_rating=0.0,
                    photo_urls=[],
                    pos_connected=False
                )
                created_cafes.append(cafe)

            serializer = CafeSerializer(created_cafes, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "error": str(e),
                "trace": traceback.format_exc()
            }, status=500)
    
class CafeImageUpdateView(APIView):
    def put(self, request):
        base_path = "/data/cafe_images/"
        idx = 0
        imageLen = 132

        cafes = Cafe.objects.all()
        for cafe in cafes:
            photo_urls = []
            for i in range(3):
                photoIndex = (idx%imageLen) + 1
                photo_url = f"{base_path}{photoIndex}.jpg"
                photo_urls.append(photo_url)
                idx += 1

            #print(f"Saving cafe {cafe.id} with images: {photo_urls}")
            cafe.photo_urls = photo_urls
            cafe.save()
            #print(f"Saved: {cafe.photo_urls}")
    
        return Response({"message": "Cafe images updated"}, status=status.HTTP_200_OK)

class CafeViewSet(viewsets.ModelViewSet):
    queryset = Cafe.objects.all().order_by('-created_at')
    serializer_class = CafeSerializer