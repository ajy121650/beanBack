from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from cafe.models import Cafe
from review.models import Review
from review.serializers import ReviewSerializer
from django.contrib.auth.models import User
from .utils.crawling import get_reviews_by_cafe_name
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from concurrent.futures import ThreadPoolExecutor, as_completed

class ReviewCrawlingView(APIView):
    @swagger_auto_schema(
        operation_id='리뷰 크롤링',
        operation_description='모든 카페에 대한 리뷰를 크롤링하여 저장합니다.',
        responses={201: "Success", 400: "Bad Request"}
    )
    def post(self, request):
        cafes = Cafe.objects.all()
        total_created = 0
        #results = []

        def crawl_reviews(cafe):
            try:
                reviews = get_reviews_by_cafe_name(cafe.name)
                created_reviews = []
                for review_text in reviews:
                    review = Review.objects.create(
                        user= None,
                        cafe=cafe,
                        content=review_text
                    )
                    created_reviews.append(review)
                return {
                    "cafe": cafe.name,
                    "review_count": len(created_reviews)
                }
            except Exception as e:
                return {
                    "cafe": cafe.name,
                    "error": str(e)
                }
        
        def save_with_retry(cafe, retry=0):
            try:
                return crawl_reviews(cafe)
            except Exception as e:
                if retry < 3:
                    print(f"[!] {cafe.name} 재시도 {retry+1}/3회")
                    return save_with_retry(cafe, retry + 1)
                else:
                    print(f"[✖] {cafe.name} 크롤링 최종 실패: {e}")
                    return {"cafe": cafe.name, "error": str(e)}
                
        
        with ThreadPoolExecutor(max_workers=3) as executor: #병렬로 3개 크롬창까지 띄움
            future_to_cafe = {executor.submit(save_with_retry, cafe): cafe for cafe in cafes}

            for future in as_completed(future_to_cafe):
                result = future.result()
                #results.append(result)
                if "review_count" in result:
                    total_created += result["review_count"]

        return Response({
            "total_reviews_created": total_created,
        }, status=status.HTTP_201_CREATED)

class ReviewListView(APIView):
    @swagger_auto_schema(
        operation_id='리뷰 목록 조회',
        operation_description='리뷰 목록을 조회합니다.',
        responses={200: ReviewSerializer(many=True)}
    )
    def get(self, request):
        reviews = Review.objects.all()
        serializer = ReviewSerializer(instance=reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ReviewDetailView(APIView):
    @swagger_auto_schema(
        operation_id='카페별 리뷰 목록 조회',
        operation_description='카페별 리뷰 목록을 조회합니다.',
        manual_parameters=[
            openapi.Parameter(
                'cafe_id', openapi.IN_PATH, 
                description="조회할 카페의 ID", 
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: ReviewSerializer(many=True)}
    )
    def get(self, request, cafe_id):
        try:
            Cafe.objects.get(pk=cafe_id)
        except Cafe.DoesNotExist:
            return Response({'detail': 'Cafe not found'}, status=status.HTTP_404_NOT_FOUND)
        reviews = Review.objects.filter(cafe_id=cafe_id)
        serializer = ReviewSerializer(instance=reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
