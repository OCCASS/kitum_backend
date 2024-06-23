from django.urls import path

from .views import *

urlpatterns = [
    path("", VariantsView.as_view(), name="variants"),
    path("<str:pk>/", VariantView.as_view(), name="variant"),
    path("<str:pk>/start/", StartVariantView.as_view(), name="start_variant"),
    path("<str:pk>/complete/", CompleteVariantView.as_view(), name="complete_variant"),
    path(
        "<str:pk>/<str:task_pk>/answer/",
        AnswerVariantTaskView.as_view(),
        name="answer_task",
    ),
    path(
        "<str:pk>/<str:task_pk>/skip/",
        SkipVariantTaskView.as_view(),
        name="answer_task",
    ),
]
