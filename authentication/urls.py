from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from .views import *

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path(
        "reset_password/",
        ResetPasswordRequestView.as_view(),
        name="request_reset_password",
    ),
    path("reset_password/check/", ResetPasswordView.as_view(), name="reset_password"),
    path("confirm_mail/", ConfirmMailView.as_view(), name="confirm_email"),
]
