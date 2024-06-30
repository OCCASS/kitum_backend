from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import *
from .serializers import *


class LessonsView(ListAPIView):
    queryset = UserLesson.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserLesson.objects.all_available_for(self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request, "without_tasks": True})
        return context


class LessonView(RetrieveAPIView):
    queryset = UserLesson.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = [IsAuthenticated, IsLessonOpened]

    def get_object(self):
        obj = self._get_lesson(self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def _get_lesson(self, pk: str) -> UserLesson:
        return UserLesson.objects.available_for_or_404(pk, self.request.user)


class CompleteLessonView(GenericAPIView):
    queryset = UserLesson.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserLessonSerializer

    def get_object(self, pk: str) -> UserLesson:
        return UserLesson.objects.available_for_or_404(pk, self.request.user)

    def post(self, request, pk: str):
        obj = self.get_object(pk)
        obj.try_complete()
        return Response(self.get_serializer(obj).data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request, "without_tasks": True})
        return context


class CompleteLessonTasksView(GenericAPIView):
    queryset = UserLesson.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserLessonSerializer

    def get_object(self, pk: str) -> UserLesson:
        return UserLesson.objects.available_for_or_404(pk, self.request.user)

    def post(self, request, pk: str):
        obj = self.get_object(pk)
        obj.try_complete_tasks()
        return Response(self.get_serializer(obj).data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class SkipLessonView(GenericAPIView):
    queryset = UserLesson.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserLessonSerializer

    def get_object(self, pk: str) -> UserLesson:
        return UserLesson.objects.available_for_or_404(pk, self.request.user)

    def post(self, request, pk: str):
        obj = self.get_object(pk)
        obj.try_skip()
        return Response(self.get_serializer(obj).data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request, "without_tasks": True})
        return context


class LessonTaskView(RetrieveAPIView):
    queryset = UserLessonTask.objects.all()
    serializer_class = UserLessonTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = get_object_or_404(
            UserLessonTask,
            task__pk=self.kwargs["task_pk"],
            lesson__lesson__pk=self.kwargs["pk"],
            lesson__user=self.request.user,
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class AnswerLessonTaskView(GenericAPIView):
    queryset = UserLessonTask.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = [IsAuthenticated]

    def get_lesson_object(self, pk: str) -> UserLesson:
        return UserLesson.objects.available_for_or_404(pk, self.request.user)

    def get_task_object(
        self, task_pk: str, lesson_pk: str, user: User
    ) -> UserLessonTask:
        return get_object_or_404(
            UserLessonTask,
            lesson__lesson__pk=lesson_pk,
            task__pk=task_pk,
            lesson__user=user,
        )

    def post(self, request, pk: str, task_pk: str):
        lesson = self.get_lesson_object(pk)

        if lesson.is_tasks_completed:
            return Response(
                {"detail": "All tasks already completed, can`t answer now."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = self.get_task_object(task_pk=task_pk, lesson_pk=pk, user=request.user)
        serializer = AnswerTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task.try_answer(serializer.data["answer"])
        return Response(self.get_serializer(lesson).data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class SkipLessonTaskView(GenericAPIView):
    queryset = UserLessonTask.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = [IsAuthenticated]

    def get_lesson_object(self, pk: str, user: User) -> UserLesson:
        return get_object_or_404(UserLesson, lesson__pk=pk, user=user)

    def get_task_object(
        self, task_pk: str, lesson_pk: str, user: User
    ) -> UserLessonTask:
        return get_object_or_404(
            UserLessonTask,
            lesson__lesson__pk=lesson_pk,
            task__pk=task_pk,
            lesson__user=user,
        )

    def post(self, request, pk: str, task_pk: str):
        lesson = self.get_lesson_object(pk, request.user)

        if lesson.is_tasks_completed:
            return Response(
                {"detail": "All tasks already completed, can`t answer now."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = self.get_task_object(task_pk=task_pk, lesson_pk=pk, user=request.user)
        task.try_skip()
        return Response(self.get_serializer(lesson).data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class HomeworkLessons(ListAPIView):
    queryset = UserLesson.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserLesson.objects.all_available_for(self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"without_tasks": True})
        return context
