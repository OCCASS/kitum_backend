from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import Response
from rest_framework.permissions import IsAuthenticated

from .exceptions import *
from .serializers import *

User = get_user_model()


class VariantsView(ListAPIView):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer

    def filter_queryset(self, queryset):
        type = self.request.query_params.get("type")
        if type is not None:
            return queryset.filter(type=type)
        return queryset


class StartVariantView(GenericAPIView):
    queryset = Variant.objects.all()

    def post(self, request, *args, **kwargs):
        variant = get_object_or_404(Variant, pk=self.kwargs["pk"])

        user_tasks = [UserTask(task=task) for task in variant.tasks.all()]
        UserTask.objects.bulk_create(user_tasks)

        user_variant = UserVariant.objects.create(
            title=variant.title,
            user=self.request.user,
            complexity=1,  # TODO: update complexity logic
        )
        user_variant.tasks.add(*user_tasks)

        return Response(UserVariantSerializer(user_variant).data)


class UserVariantsView(ListAPIView):
    """Список вариантов"""

    queryset = UserVariant.objects.all()
    serializer_class = UserVariantWithoutTasksSerializer

    def filter_queryset(self, queryset):
        queryset = queryset.filter(user=self.request.user)

        generated = self.request.query_params.get("generated")
        if generated is not None:
            queryset = queryset.filter(generated=generated == "true")
        status = self.request.query_params.get("status")
        if status is not None:
            queryset = queryset.filter(status=status)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class UserVariantView(RetrieveAPIView):
    """Отдельный вариант"""

    queryset = UserVariant.objects.all()
    serializer_class = UserVariantSerializer

    def get_object(self):
        obj = get_object_or_404(
            UserVariant, pk=self.kwargs["pk"], user=self.request.user
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class StartUserVariantView(GenericAPIView):
    queryset = UserVariant.objects.all()
    serializer_class = UserVariantSerializer

    def post(self, request, *args, **kwargs):
        variant = self.get_object()
        variant.start()
        return Response(self.get_serializer(variant).data)

    def get_object(self) -> UserVariant:
        variant = get_object_or_404(
            UserVariant, pk=self.kwargs["pk"], user=self.request.user
        )
        self.check_object_permissions(self.request, variant)
        return variant

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class CompleteUserVariantView(GenericAPIView):
    serializer_class = UserVariantSerializer

    def get_object(self) -> UserVariant:
        obj = get_object_or_404(
            UserVariant, pk=self.kwargs["pk"], user=self.request.user
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


class AnswerUserVariantTaskView(GenericAPIView):
    serializer_class = UserVariantSerializer

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
            UserVariant, pk=self.kwargs["pk"], user=self.request.user
        )

    def _validate_started_and_not_completed(self, variant: UserVariant):
        if not variant.is_started:
            raise VariantNotStarted
        if variant.is_completed:
            raise VariantCompleted

    def _get_user_variant_task_or_fail(self, variant: UserVariant):
        task_id = self.kwargs["task_pk"]
        if not variant.tasks.filter(pk=task_id).exists():
            raise VariantNotIncludesTask

        return get_object_or_404(UserTask, pk=task_id)

    def _try_to_answer_task(self, task: UserTask):
        answer_data = self._get_answer_data()
        if not answer_data or not all(answer_data):
            raise AnswerIsEmptyError
        task.try_answer(answer_data)

    def _get_answer_data(self) -> list:
        serializer = AnswerTaskSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data.get("answer", [])


class SkipUserVariantTaskView(GenericAPIView):
    serializer_class = UserVariantSerializer

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
            UserVariant, pk=self.kwargs["pk"], user=self.request.user
        )

    def _validate_started_and_not_completed(self, variant: UserVariant):
        if not variant.is_started:
            raise VariantNotStarted
        if variant.is_completed:
            raise VariantCompleted

    def _get_user_variant_task_or_fail(self, variant: UserVariant):
        task_id = self.kwargs["task_pk"]
        if not variant.tasks.filter(pk=task_id).exists():
            raise VariantNotIncludesTask

        return get_object_or_404(UserTask, pk=task_id)


"""
class GenerateVariantView(GenericAPIView):
    serializer_class = GenerateVariantSerializer
    permission_classes = (IsAuthenticated, IsUserHaveSubscription)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        variant = self._generate_variant(
            serializer.data["name"], serializer.data["complexity"]
        )
        return Response(UserVariantSerializer(variant).data, status=200)

    def _generate_variant(self, name: str, complexity: int):
        variant = UserVariant(
            title=name, user=self.request.user, complexity=complexity, generated=True
        )
        variant.save()
        sorted_tasks = Task.objects.all()

        tasks_by_kim_number = {}
        for task in sorted_tasks:
            tasks_by_kim_number.setdefault(task.kim_number, []).append(task)

        tasks = []
        for n in range(min_kim_number, max_kim_number + 1):
            if n in tasks_by_kim_number:
                task = random.choice(tasks_by_kim_number[n])
                tasks.append(UserTask(task=task))

        UserTask.objects.bulk_create(tasks)
        variant.tasks.add(*tasks)
        variant.save()
        return variant
    """
