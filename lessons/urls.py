from django.urls import path

from .views import *

urlpatterns = [
    path("", LessonsView.as_view(), name="lessons"),
    path("homework/", HomeworkLessons.as_view(), name="homework"),
    path("<str:pk>/", LessonView.as_view(), name="lesson"),
    path(
        "<str:pk>/complete/",
        CompleteLessonView.as_view(),
        name="complete_lesson",
    ),
    path(
        "<str:pk>/complete_tasks/",
        CompleteLessonTasksView.as_view(),
        name="complete_lesson",
    ),
    path("<str:pk>/skip/", SkipLessonView.as_view(), name="skip_lesson"),
    path(
        "<str:pk>/<str:task_pk>/",
        LessonTaskView.as_view(),
        name="task",
    ),
    path(
        "<str:pk>/<str:task_pk>/answer/",
        AnswerLessonTaskView.as_view(),
        name="answer_task",
    ),
    path(
        "<str:pk>/<str:task_pk>/skip/",
        SkipLessonTaskView.as_view(),
        name="skip_task",
    ),
]
