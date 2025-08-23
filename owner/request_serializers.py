from rest_framework import serializers

# 회원가입 요청 시 필요한 데이터(username, password)를 검증하는 Serializer
class SignUpRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

# 로그인 요청 시 필요한 데이터(username, password)를 검증하는 Serializer
class SignInRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

# refresh token을 검증하는 Serializer
class TokenRefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()

