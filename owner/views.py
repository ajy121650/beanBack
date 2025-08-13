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
from owner.models import Owner
from .serializers import UserSerializer, OwnerSerializer
from .request_serializers import SignUpRequestSerializer, SignInRequestSerializer 
from rest_framework_simplejwt.tokens import RefreshToken #추가

def set_token_on_response_cookie(user, status_code):
    token = RefreshToken.for_user(user)
    owner = Owner.objects.get(user=user)
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
            
        owner = Owner.objects.create(
            user=user
        )

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


class OwnerDetailCafeListView(APIView):
    def get(self, request, owner_id):
        try:
            owner = Owner.objects.get(id=owner_id)
        except Owner.DoesNotExist:
            return Response({"error": "Owner not found"}, status=status.HTTP_404_NOT_FOUND)

        cafes = Cafe.objects.filter(owner=owner)
        serializer = CafeSerializer(cafes, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

