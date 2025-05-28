from django.urls import path

from .views import *

urlpatterns = [
    path("", VariantsView.as_view(), name="variant_list"),
    path("<uuid:pk>/start/", StartVariantView.as_view(), name="start_variant"),
    path("my/", UserVariantsView.as_view(), name="user_variant_list"),
    # path("generate/", GenerateVariantView.as_view(), name="generated_variant_create"),
    path("my/<uuid:pk>/", UserVariantView.as_view(), name="user_variant_detail"),
    path(
        "my/<uuid:pk>/start/", StartUserVariantView.as_view(), name="user_variant_start"
    ),
    path(
        "my/<uuid:pk>/complete/",
        CompleteUserVariantView.as_view(),
        name="user_variant_complete",
    ),
    path(
        "my/<uuid:pk>/<uuid:task_pk>/answer/",
        AnswerUserVariantTaskView.as_view(),
        name="user_variant_task_answer",
    ),
    path(
        "my/<uuid:pk>/<uuid:task_pk>/skip/",
        SkipUserVariantTaskView.as_view(),
        name="user_variant_task_skip",
    ),
]
