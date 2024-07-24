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
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserLesson.objects.all_available_for(self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request, "without_tasks": True})
        return context


class NotCompletedLessonsView(ListAPIView):
    queryset = UserLesson.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserLesson.objects.all_available_for(self.request.user).filter(
            ~models.Q(status=UserLesson.COMPLETED) & ~models.Q(status=UserLesson.TASKS_COMPLETED)
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request, "without_tasks": True})
        return context


class LessonView(RetrieveAPIView):
    queryset = UserLesson.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = (IsAuthenticated, IsLessonOpened)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_object(self):
        pk = self.kwargs["pk"]
        obj = UserLesson.objects.available_for_or_404(pk, self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj


class CompleteLessonView(GenericAPIView):
    queryset = UserLesson.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserLessonSerializer

    def post(self, request, *args, **kwargs):
        lesson = self.get_object()
        lesson.try_complete()
        return Response(self.get_serializer(lesson).data)

    def get_object(self) -> UserLesson:
        pk = self.kwargs["pk"]
        obj = UserLesson.objects.available_for_or_404(pk, self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request, "without_tasks": True})
        return context


class CompleteLessonTasksView(GenericAPIView):
    queryset = UserLesson.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserLessonSerializer

    def post(self, request, *args, **kwargs):
        lesson = self.get_object()
        lesson.try_complete_tasks()
        return Response(self.get_serializer(lesson).data)

    def get_object(self) -> UserLesson:
        pk = self.kwargs["pk"]
        obj = UserLesson.objects.available_for_or_404(pk, self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class LessonTaskView(RetrieveAPIView):
    queryset = UserTask.objects.all()
    serializer_class = UserTask
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class AnswerLessonTaskView(GenericAPIView):
    queryset = UserTask.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        lesson = self._get_user_lesson_or_fail()
        self._validate_tasks_not_completed(lesson)

        task = self._get_user_lesson_task_or_fail(lesson)
        self._try_to_answer_task(task)

        serialized_lesson = self.get_serializer(lesson)
        return Response(serialized_lesson.data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def _get_user_lesson_or_fail(self):
        pk = self.kwargs["pk"]
        lesson = UserLesson.objects.available_for_or_404(pk, self.request.user)
        self.check_object_permissions(self.request, lesson)
        return lesson

    def _validate_tasks_not_completed(self, lesson: UserLesson):
        if lesson.status == UserLesson.TASKS_COMPLETED:
            raise LessonTasksAlreadyCompleted

    def _get_user_lesson_task_or_fail(self, lesson: UserLesson) -> UserTask:
        task_id = self.kwargs["task_pk"]
        if not lesson.tasks.filter(pk=task_id).exists():
            raise LessonNotIncludesTask

        task = get_object_or_404(UserTask, pk=task_id)
        self.check_object_permissions(self.request, task)
        return task

    def _try_to_answer_task(self, task: UserTask):
        answer_data = self._get_answer_data()
        if not answer_data or not all(answer_data):
            raise AnswerIsEmptyError
        task.try_answer(answer_data)

    def _get_answer_data(self) -> list:
        serializer = AnswerTaskSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data.get("answer", [])


class SkipLessonTaskView(GenericAPIView):
    queryset = UserTask.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        lesson = self._get_user_lesson_or_fail()
        self._validate_tasks_not_completed(lesson)

        task = self._get_user_lesson_task_or_fail(lesson)
        task.try_skip()

        serialized_lesson = self.get_serializer(lesson)
        return Response(serialized_lesson.data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def _get_user_lesson_or_fail(self):
        pk = self.kwargs["pk"]
        lesson = UserLesson.objects.available_for_or_404(pk, self.request.user)
        self.check_object_permissions(self.request, lesson)
        return lesson

    def _validate_tasks_not_completed(self, lesson: UserLesson):
        if lesson.status == UserLesson.TASKS_COMPLETED:
            raise LessonTasksAlreadyCompleted

    def _get_user_lesson_task_or_fail(self, lesson: UserLesson) -> UserTask:
        task_id = self.kwargs["task_pk"]
        if not lesson.tasks.filter(pk=task_id).exists():
            raise LessonNotIncludesTask

        task = get_object_or_404(UserTask, pk=task_id)
        self.check_object_permissions(self.request, task)
        return task


class HomeworkLessons(ListAPIView):
    queryset = UserLesson.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserLesson.objects.all_available_for(self.request.user).filter(
            models.Q(status=UserLesson.COMPLETED) | models.Q(status=UserLesson.TASKS_COMPLETED)
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"without_tasks": True})
        return context


class NotCompletedHomeworkLessons(ListAPIView):
    queryset = UserLesson.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserLesson.objects.all_available_for(self.request.user).filter(
            status=UserLesson.COMPLETED
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"without_tasks": True})
        return context
