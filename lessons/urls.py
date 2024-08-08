from django.urls import path

from .views import *

urlpatterns = [
    path("", LessonsView.as_view(), name="lesson_list"),
    path(
        "not_completed/",
        NotCompletedLessonsView.as_view(),
        name="lesson_not_completed_list",
    ),
    path("homework/", HomeworkLessons.as_view(), name="homework_list"),
    path(
        "homework/not_completed/",
        NotCompletedHomeworkLessons.as_view(),
        name="homework_list",
    ),
    path("<uuid:pk>/", LessonView.as_view(), name="lesson_detail"),
    path(
        "<uuid:pk>/complete/",
        CompleteLessonView.as_view(),
        name="lesson_complete",
    ),
    path(
        "<uuid:pk>/complete_tasks/",
        CompleteLessonTasksView.as_view(),
        name="lesson_tasks_complete",
    ),
    path(
        "<uuid:pk>/<uuid:task_pk>/",
        LessonTaskView.as_view(),
        name="task_detail",
    ),
    path(
        "<uuid:pk>/<uuid:task_pk>/answer/",
        AnswerLessonTaskView.as_view(),
        name="task_answer",
    ),
    path(
        "<uuid:pk>/<uuid:task_pk>/skip/",
        SkipLessonTaskView.as_view(),
        name="task_skip",
    ),
]
