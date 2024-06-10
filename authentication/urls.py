from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from .views import *

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", CookieTokenObtainPairView.as_view(), name="login"),
    path("refresh/", CookieTokenRefreshView.as_view(), name="refresh_token"),
    path("logout/", CookieTokenBlackListView.as_view(), name="logout"),
    path("verify_token/", jwt_views.TokenVerifyView.as_view(), name="verify_token"),
]
