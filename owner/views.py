from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import auth
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from cafe.models import Cafe
from cafe.serializers import CafeSerializer
from .models import Owner
from .serializers import (
    UserIdUsernameSerializer, 
    UserSerializer, 
    OwnerSerializer
)
from .request_serializers import (
    SignUpRequestSerializer, 
    SignInRequestSerializer, 
    TokenRefreshRequestSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken #추가

def set_token_on_response_cookie(user, status_code):
    token = RefreshToken.for_user(user)
    owner = Owner.objects.get(owner=user)
    serialized_data = OwnerSerializer(owner).data
    res = Response(serialized_data, status=status_code)
    res.set_cookie("refresh_token", value=str(token), httponly=True)
    res.set_cookie("access_token", value=str(token.access_token), httponly=True)
    return res

class SignUpView(APIView):
    @swagger_auto_schema(
        operation_id="회원가입",
        operation_description="회원가입을 진행합니다.",
        request_body=SignUpRequestSerializer,
        responses={201: "JWT Token 발급", 400: "Bad Request"},
    )
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()
            user.set_password(user.password)
            user.save()
            
        Owner.objects.create( owner=user )
        return set_token_on_response_cookie(user, status_code=status.HTTP_201_CREATED)
        
class SignInView(APIView):
    @swagger_auto_schema(
        operation_id="로그인",
        operation_description="로그인을 진행합니다.",
        request_body=SignInRequestSerializer,
        responses={200: UserSerializer, 404: "Not Found", 400: "Bad Request"},
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"detail": "username/password required"}, status=400)
        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                return Response(
                    {"message": "Password is incorrect"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return set_token_on_response_cookie(user, status_code=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

class TokenRefreshView(APIView):
    @swagger_auto_schema(
        operation_id="토큰 재발급",
        operation_description="access 토큰을 재발급 받습니다.",
        request_body=TokenRefreshRequestSerializer,
        responses={200: OwnerSerializer},
    )
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "no refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            RefreshToken(refresh_token).verify()
        except:
            return Response(
                {"detail": "please signin again."}, status=status.HTTP_401_UNAUTHORIZED
            )
        new_access_token = str(RefreshToken(refresh_token).access_token)
        response = Response({"detail": "token refreshed"}, status=status.HTTP_200_OK)
        response.set_cookie("access_token", value=str(new_access_token), httponly=True, samesite='Strict')
        return response


class SignOutView(APIView):
    @swagger_auto_schema(
        operation_id="로그아웃",
        operation_description="로그아웃을 진행합니다.",
        responses={204: "No Content"},
    )
    def post(self, request):

        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "no refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )
        RefreshToken(refresh_token).blacklist()

        res = Response(status=status.HTTP_204_NO_CONTENT)
        res.delete_cookie("access_token")
        res.delete_cookie("refresh_token")
        return res

class UserInfoView(APIView):
    @swagger_auto_schema(
        operation_id="사용자 정보 조회",
        operation_description="현재 로그인한 사용자의 정보를 조회합니다.",
        responses={
            200: UserIdUsernameSerializer,
            401: 'Unauthorized'
        }
    )
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "로그인 후 다시 시도해주세요."}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        serializer = UserIdUsernameSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class OwnerDetailCafeListView(APIView):
    @swagger_auto_schema(
        operation_id="오너의 카페 리스트 조회",
        operation_description="owner_id에 해당하는 오너가 소유한 모든 카페 리스트를 반환합니다.",
        responses={200: CafeSerializer(many=True), 404: "Owner not found"},
        manual_parameters=[
            openapi.Parameter(
                'owner_id',
                openapi.IN_PATH,
                description="Owner의 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    def get(self, request, owner_id):
        try:
            owner = Owner.objects.get(id=owner_id)
        except Owner.DoesNotExist:
            return Response({"error": "Owner not found"}, status=status.HTTP_404_NOT_FOUND)

        cafes = Cafe.objects.filter(owner=owner)
        serializer = CafeSerializer(cafes, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

