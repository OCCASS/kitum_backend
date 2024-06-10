from django.urls import path

from .views import *

urlpatterns = [
    path("", LessonsView.as_view(), name="lessons"),
    path("user/<str:user>/", UserLessonsView.as_view(), name="user_lessons"),
]
