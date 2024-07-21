from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.mixins import Response
from rest_framework.permissions import IsAuthenticated

from .exceptions import VariantCompleted, VariantNotStarted
from .serializers import *

User = get_user_model()


class VariantsView(ListAPIView):
    """Список вариантов"""

    queryset = UserVariant.objects.all()
    serializer_class = UserVariantWithoutTasksSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class VariantView(RetrieveAPIView):
    """Отдельный вариант"""

    queryset = UserVariant.objects.all()
    serializer_class = UserVariantSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        obj = get_object_or_404(
            UserVariant,
            variant__pk=self.kwargs["pk"],
            user=self.request.user,
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class StartVariantView(GenericAPIView):
    queryset = UserVariant.objects.all()
    serializer_class = UserVariantSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        variant = self.get_object()
        variant.start()
        return Response(self.get_serializer(variant).data)

    def get_object(self) -> UserVariant:
        variant = get_object_or_404(
            UserVariant, variant__pk=self.kwargs["pk"], user=self.request.user
        )
        self.check_object_permissions(self.request, variant)
        return variant

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class CompleteVariantView(GenericAPIView):
    serializer_class = UserVariantSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> UserVariant:
        obj = get_object_or_404(
            UserVariant, variant__pk=self.kwargs["pk"], user=self.request.user
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.complete()
        return Response(self.get_serializer(obj).data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class AnswerVariantTaskView(GenericAPIView):
    serializer_class = UserVariantSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        variant = self._get_user_variant_or_fail()
        self._validate_started_and_not_completed(variant)

        task = self._get_user_variant_task_or_fail(variant)
        self._try_to_answer_task(task)

        serialized_variant = self.get_serializer(variant)
        return Response(serialized_variant.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def _get_user_variant_or_fail(self):
        return get_object_or_404(
            UserVariant, variant__pk=self.kwargs["pk"], user=self.request.user
        )

    def _validate_started_and_not_completed(self, variant: UserVariant):
        if not variant.is_started:
            raise VariantNotStarted
        if variant.is_completed:
            raise VariantCompleted

    def _get_user_variant_task_or_fail(self, variant: UserVariant):
        return get_object_or_404(variant.tasks, pk=self.kwargs["pk"])

    def _try_to_answer_task(self, task: UserVariantTask):
        answer_data = self._get_answer_data()
        task.try_answer(answer_data)

    def _get_answer_data(self) -> list:
        serializer = AnswerTaskSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data.get("answer", [])


class SkipVariantTaskView(GenericAPIView):
    serializer_class = UserVariantSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        variant = self._get_user_variant_or_fail()
        self._validate_started_and_not_completed(variant)

        task = self._get_user_variant_task_or_fail()
        task.try_skip()

        serialized_variant = self.get_serializer(variant)
        return Response(serialized_variant.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def _get_user_variant_or_fail(self):
        return get_object_or_404(
            UserVariant, variant__pk=self.kwargs["pk"], user=self.request.user
        )

    def _validate_started_and_not_completed(self, variant: UserVariant):
        if not variant.is_started:
            raise VariantNotStarted
        if variant.is_completed:
            raise VariantCompleted

    def _get_user_variant_task_or_fail(self):
        return get_object_or_404(
            UserVariantTask,
            variant__variant__pk=self.kwargs["pk"],
            task__pk=self.kwargs["task_pk"],
            variant__user=self.request.user,
        )


class GenerateVariant(GenericAPIView):
    serializer_class = GenerateVariantSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        serializer.validate(raise_exception=True)
