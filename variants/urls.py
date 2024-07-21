from django.urls import path

from .views import *

urlpatterns = [
    path("", VariantsView.as_view(), name="variant_list"),
    path("generate/", GenerateVariantView.as_view(), name="variant_generate"),
    path("<str:pk>/", VariantView.as_view(), name="variant_detail"),
    path("<str:pk>/start/", StartVariantView.as_view(), name="variant_start"),
    path("<str:pk>/complete/", CompleteVariantView.as_view(), name="variant_complete"),
    path(
        "<str:pk>/<str:task_pk>/answer/",
        AnswerVariantTaskView.as_view(),
        name="task_answer",
    ),
    path(
        "<str:pk>/<str:task_pk>/skip/",
        SkipVariantTaskView.as_view(),
        name="task_skip",
    ),
]
