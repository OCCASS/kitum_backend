from user.serializers import UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer,
)

User = get_user_model()


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        user: User = self.user

        if not user.is_confirmed:
            raise serializers.ValidationError(
                "User account is not confirmed.", code="authorization"
            )

        seriazlier = UserSerializer(user, context=self.context)
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


class ConfirmMailSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
