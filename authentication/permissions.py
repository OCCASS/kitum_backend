from typing import cast

from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import AccessToken

from authentication.utils import get_client_ip
from user.models import UserSession


class OneDevicePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            raise NotAuthenticated

        try:
            user_session = UserSession.objects.get(user=user, is_active=True)
        except UserSession.DoesNotExist:
            raise NotAuthenticated

        token: AccessToken = cast(AccessToken, request.auth)
        ip = get_client_ip(request)
        fingerprint = request.headers.get("X-Fingerprint")
        if (
            token.get("jti") != user_session.jti
            or ip != user_session.ip_address
            or fingerprint != user_session.fingerprint
        ):
            raise NotAuthenticated

        return True
