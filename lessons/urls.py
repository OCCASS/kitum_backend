from django.urls import path

from .views import *

urlpatterns = [
    path("", LessonsView.as_view(), name="lesson_list"),
    path("homework/", HomeworkLessons.as_view(), name="homework_list"),
    path("<str:pk>/", LessonView.as_view(), name="lesson_detail"),
    path(
        "<str:pk>/complete/",
        CompleteLessonView.as_view(),
        name="lesson_complete",
    ),
    path(
        "<str:pk>/complete_tasks/",
        CompleteLessonTasksView.as_view(),
        name="lesson_tasks_complete",
    ),
    path("<str:pk>/skip/", SkipLessonView.as_view(), name="lesson_skip"),
    path(
        "<str:pk>/<str:task_pk>/",
        LessonTaskView.as_view(),
        name="task_detail",
    ),
    path(
        "<str:pk>/<str:task_pk>/answer/",
        AnswerLessonTaskView.as_view(),
        name="task_answer",
    ),
    path(
        "<str:pk>/<str:task_pk>/skip/",
        SkipLessonTaskView.as_view(),
        name="task_skip",
    ),
]
