from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer,
)
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.utils import get_client_ip
from user.models import UserSession
from user.serializers import UserSerializer

User = get_user_model()


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    def validate(self, attrs):
        request = self.context["request"]
        fingerprint = request.headers.get("X-Fingerprint")
        user_agent = request.headers.get("User-Agent")
        ip = get_client_ip(request)

        attrs = super().validate(attrs)
        user: User = self.user

        if not user.is_confirmed:
            raise serializers.ValidationError(
                "User account is not confirmed.", code="authorization"
            )

        # Blacklist existing tokens BEFORE creating new ones
        refresh: RefreshToken = self.token_class(attrs.get("refresh"))
        self.deactivate_outstanding_tokens(refresh)

        UserSession.objects.filter(user=user, is_active=True).update(is_active=False)

        access = AccessToken(attrs.get("access"))
        UserSession.objects.create(
            user=user,
            jti=access["jti"],
            user_agent=user_agent,
            fingerprint=fingerprint,
            ip_address=ip,
        )

        serializer = UserSerializer(user, context=self.context)
        return {"user": serializer.data, **attrs}

    def deactivate_outstanding_tokens(self, new_refresh: RefreshToken):
        """Blacklist all existing outstanding tokens for this user"""
        tokens = OutstandingToken.objects.filter(
            user=self.user, expires_at__gt=now()
        ).exclude(jti=new_refresh["jti"])
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

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
