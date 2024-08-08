from django.urls import path

from .views import *

urlpatterns = [
    path("", VariantsView.as_view(), name="variant_list"),
    path("generate/", GenerateVariantView.as_view(), name="generated_variant_create"),
    path("<uuid:pk>/", VariantView.as_view(), name="variant_detail"),
    path("<uuid:pk>/start/", StartVariantView.as_view(), name="variant_start"),
    path("<uuid:pk>/complete/", CompleteVariantView.as_view(), name="variant_complete"),
    path(
        "<uuid:pk>/<uuid:task_pk>/answer/",
        AnswerVariantTaskView.as_view(),
        name="task_answer",
    ),
    path(
        "<uuid:pk>/<uuid:task_pk>/skip/",
        SkipVariantTaskView.as_view(),
        name="task_skip",
    ),
]
