from typing import Literal, TypeAlias

from core.serializers import UserSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import send_mail
from django.contrib.auth.tokens import (
    PasswordResetTokenGenerator,
    default_token_generator,
)
from django.http import Http404
from django.utils import timezone
from rest_framework import permissions, serializers
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
)

from .exceptions import ConfirmMailTokenIsInvalid, PasswordResetRequestAlreadyCreated
from .models import ConfirmMail, PasswordReset
from .serializers import (
    ConfirmMailSerializer,
    ResetPasswordRequestSerializer,
    ResetPasswordSerializer,
    TokenObtainPairSerializer,
)

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
        self._send_confirmation_mail(user)
        return self._create_response(tokens, serializer.data)

    def _create_response(self, tokens: TokensDict, data: dict) -> Response:
        data = self._build_response_data(data, tokens)
        return Response(data)

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
    def _build_response_data(user_data: dict, tokens: TokensDict) -> dict:
        return {"user": user_data, **tokens}

    def _send_confirmation_mail(self, user: User):
        token = default_token_generator.make_token(user)
        ConfirmMail(user=user, token=token).save()
        url = f"{settings.CONFIRM_MAIL_BASE_URL}/?t={token}"
        send_mail(
            "KITUM – подтверждение почты",
            url,
            settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
        )


class TokenObtainPairView(BaseTokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class ResetPasswordRequestView(GenericAPIView):
    serializer_class = ResetPasswordRequestSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        if not self._can_reset(email):
            raise PasswordResetRequestAlreadyCreated
        token = self._create_token_for_user(email)
        reset_url = f"{settings.PASSWORD_RESET_BASE_URL}/?t={token}"
        send_mail(
            "KITUM – сброс пароля",
            f"Ссылка для сбороса пароля – {reset_url}",
            settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )
        return Response()

    def _can_reset(self, email: str) -> bool:
        return not PasswordReset.objects.filter(
            email=email, expires_at__gt=timezone.now()
        ).exists()

    def _create_token_for_user(self, email: str) -> str:
        user = get_object_or_404(User, email=email)
        token = self._generate_token(user)
        PasswordReset(email=email, token=token).save()
        return token

    def _generate_token(self, user: User) -> str:
        token_generator = PasswordResetTokenGenerator()
        return token_generator.make_token(user)


class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self._update_token_owner_password(
            serializer.validated_data["token"],
            serializer.validated_data["new_password"],
        )
        return Response()

    def _update_token_owner_password(self, token: str, new_password: str) -> None:
        reset_obj = get_object_or_404(
            PasswordReset, token=token, expires_at__gt=timezone.now()
        )
        self._update_user_password(reset_obj.email, new_password)

    def _update_user_password(self, email: str, new_password: str) -> None:
        user = get_object_or_404(User, email=email)
        user.set_password(new_password)
        user.save()


class ConfirmMailView(GenericAPIView):
    serializer_class = ConfirmMailSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self._confirm_token_owner_email(serializer.validated_data["token"])
        return Response()

    def _confirm_token_owner_email(self, token: str) -> None:
        confirm_obj = (
            ConfirmMail.objects.select_related("user")
            .filter(token=token, expires_at__gt=timezone.now())
            .first()
        )
        if confirm_obj is None:
            raise ConfirmMailTokenIsInvalid
        self._confirm_user_email(confirm_obj.user.email)
        confirm_obj.delete()

    def _confirm_user_email(self, email: str):
        user = get_object_or_404(User, email=email)
        user.is_confirmed = True
        user.save()
