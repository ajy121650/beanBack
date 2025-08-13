from rest_framework import serializers


class SignUpRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class SignInRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
