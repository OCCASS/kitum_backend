from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer,
)

from core.serializers import UserSerializer

User = get_user_model()


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        seriazlier = UserSerializer(self.user, context=self.context)
        return {"user": seriazlier.data, **attrs}

    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token["is_staff"] = user.is_staff
        return token


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    token = serializers.CharField(required=True)
