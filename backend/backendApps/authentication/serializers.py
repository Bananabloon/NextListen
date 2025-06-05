from rest_framework import serializers


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()


class ErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()


class EmptyRequestSerializer(serializers.Serializer):
    pass
