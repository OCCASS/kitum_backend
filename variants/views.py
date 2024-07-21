import random
from sys import set_coroutine_origin_tracking_depth

from django.db.models import Min
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
        return get_object_or_404(variant.tasks, pk=self.kwargs["task_pk"])

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

        task = self._get_user_variant_task_or_fail(variant)
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

    def _get_user_variant_task_or_fail(self, variant: UserVariant):
        return get_object_or_404(variant.tasks, pk=self.kwargs["task_pk"])


class GenerateVariantView(GenericAPIView):
    serializer_class = GenerateVariantSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        variant = self._generate_variant(serializer.data["name"], serializer.data["complexity"])
        return Response(GeneratedVariantSerializer(variant).data, status=200)

    def _generate_variant(self, name: str, complexity: int):
        variant = GeneratedUserVariant(
            title=name, user=self.request.user, complexity=complexity
        )
        variant.save()
        sorted_tasks = Task.objects.all().order_by("kim_number")
        min_kim_number = sorted_tasks.first().kim_number
        max_kim_number = sorted_tasks.last().kim_number
        for n in range(min_kim_number, max_kim_number + 1):
            ids = Task.objects.filter(kim_number=n, complexity=complexity).values_list("id")
            if ids:
                task = Task.objects.get(pk=random.choice(ids)[0])
                user_task = UserVariantTask(task=task)
                user_task.save()
                variant.tasks.add(user_task)
        variant.save()
        return variant
