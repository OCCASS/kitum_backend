from django.core.files.uploadedfile import UploadedFile
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import FormParser
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import *
from .serializers import *
from authentication.permissions import OneDevicePermission
from tasks.models import UserTask


class LessonsView(ListAPIView):
    queryset = UserLesson.objects.all()
    serializer_class = UserLessonSerializer

    def get_queryset(self):
        return UserLesson.objects.filter(user=self.request.user)

    def filter_queryset(self, queryset):
        status = self.request.query_params.get("status")
        if status is not None and status != "":
            queryset = queryset.filter(status=status)
        subscription = self.request.query_params.get("subscription")
        if subscription is not None and subscription != "":
            queryset = queryset.filter(lesson__subscription=subscription)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request, "without_tasks": True})
        return context


class NotCompletedLessonsView(ListAPIView):
    queryset = UserLesson.objects.all()
    serializer_class = UserLessonSerializer

    def get_queryset(self):
        return UserLesson.objects.all_available_for(self.request.user).filter(
            ~models.Q(status=UserLesson.COMPLETED)
            & ~models.Q(status=UserLesson.TASKS_COMPLETED)
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request, "without_tasks": True})
        return context


class LessonView(RetrieveAPIView):
    queryset = UserLesson.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = (IsAuthenticated, OneDevicePermission, IsLessonOpened)

    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

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
    permission_classes = (IsAuthenticated, OneDevicePermission, HaveHomeworkAccess)
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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class AnswerLessonTaskView(GenericAPIView):
    queryset = UserTask.objects.all()
    serializer_class = UserLessonSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = (IsAuthenticated, OneDevicePermission, HaveHomeworkAccess)

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
        if not answer_data:
            raise AnswerIsEmptyError
        task.try_answer(answer_data)

    def _get_answer_data(self) -> str | UploadedFile:
        serializer = AnswerTaskSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if "answer" in data:
            return data["answer"]
        else:
            return data["answer_file"]


class SkipLessonTaskView(GenericAPIView):
    queryset = UserTask.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = (IsAuthenticated, OneDevicePermission, HaveHomeworkAccess)

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
    permission_classes = (IsAuthenticated, OneDevicePermission, HaveHomeworkAccess)

    def get_queryset(self):
        return UserLesson.objects.all_available_for(self.request.user).filter(
            models.Q(status=UserLesson.COMPLETED)
            | models.Q(status=UserLesson.TASKS_COMPLETED)
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request, "without_tasks": True})
        return context


class NotCompletedHomeworkLessons(ListAPIView):
    queryset = UserLesson.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = (IsAuthenticated, OneDevicePermission, HaveHomeworkAccess)

    def get_queryset(self):
        return UserLesson.objects.all_available_for(self.request.user).filter(
            status=UserLesson.COMPLETED
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request, "without_tasks": True})
        return context


class AvailableSubscriptionsView(APIView):
    def get(self, request):
        subscriptions = (
            UserLesson.objects.filter(user=request.user)
            .select_related("lesson__subscription")
            .values_list("lesson__subscription", flat=True)
            .distinct()
        )

        subs = Subscription.objects.filter(id__in=subscriptions)
        serializer = SubscriptionSerializer(subs, many=True)
        return Response(serializer.data)
