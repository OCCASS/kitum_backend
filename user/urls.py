from django.urls import path

from .views import *

urlpatterns = [
    path("me/", UserView.as_view(), name="user"),
    path("me/edit/", EditUserView.as_view(), name="user_edit"),
    path("me/edit_avatar/", EditUserAvatarView.as_view(), name="user_edit_avatar"),
]
