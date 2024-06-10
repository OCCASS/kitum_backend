from typing import Literal, TypeAlias

from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from config import settings
from core.serializers import UserSerializer

from .serializers import CookieTokenBlackListSerializer, CookieTokenRefreshSerializer

User = get_user_model()
TokensDict: TypeAlias = dict[Literal["access", "refresh"], str]


class RegistrationView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self._perform_create(serializer)
        tokens = self._get_user_tokens(user)
        return self._create_response(tokens, serializer.data)

    def _create_response(self, tokens: TokensDict, data: dict) -> Response:
        data = self._build_response_data(data, tokens["access"])
        response = Response(data, status=status.HTTP_201_CREATED)
        response.set_cookie(
            "refresh",
            tokens["refresh"],
            max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].seconds,
            httponly=True,
        )
        return response

    @staticmethod
    def _perform_create(serializer: UserSerializer) -> User:
        """Performer model creation from serializer"""
        return serializer.save()

    @staticmethod
    def _get_user_tokens(user: User) -> TokensDict:
        """Get user JWT tokens dict like {'access': '...', 'refresh': '...'}"""
        token = RefreshToken.for_user(user)
        return {"access": str(token.access_token), "refresh": str(token)}

    @staticmethod
    def _build_response_data(user_data: dict, access_token: str) -> dict:
        return {"user": user_data, "access": access_token}


class CookieTokenObtainPairView(TokenObtainPairView):
    def finalize_response(self, request: Request, response: Response, *args, **kwargs):
        if refresh_token := response.data.pop("refresh", None):
            cookie_max_age = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].seconds
            response.set_cookie(
                "refresh", refresh_token, max_age=cookie_max_age, httponly=True
            )

        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request: Request, response: Response, *args, **kwargs):
        if refresh_token := response.data.pop("refresh", None):
            cookie_max_age = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].seconds
            response.set_cookie(
                "refresh", refresh_token, max_age=cookie_max_age, httponly=True
            )
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenBlackListView(TokenBlacklistView):
    serializer_class = CookieTokenBlackListSerializer

    def finalize_response(self, request: Request, response: Response, *args, **kwargs):
        response.cookies.pop("refresh", None)
        return super().finalize_response(request, response, *args, **kwargs)
