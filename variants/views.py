from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.mixins import Response, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import *
from .serializers import *

User = get_user_model()


class VariantsView(ListAPIView):
    """Список вариантов"""

    queryset = UserVariant.objects.all()
    serializer_class = UserVariantWithoutTasksSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class VariantView(RetrieveAPIView):
    """Отдельный вариант"""

    queryset = UserVariant.objects.all()
    serializer_class = UserVariantSerializer
    permission_classes = [IsAuthenticated]

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


class StartVariantView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk: str, user: User) -> UserVariant:
        return get_object_or_404(UserVariant, variant__pk=pk, user=user)

    def post(self, request, pk: str):
        obj = self.get_object(pk, request.user)
        obj.start()
        return Response(UserVariantSerializer(obj, context={"request": request}).data)


class CompleteVariantView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk: str, user: User) -> UserVariant:
        return get_object_or_404(UserVariant, variant__pk=pk, user=user)

    def post(self, request, pk: str):
        obj = self.get_object(pk, request.user)
        obj.complete()
        return Response(UserVariantSerializer(obj, context={"request": request}).data)


class AnswerVariantTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get_variant_object(self, pk: str, user: User) -> UserVariant:
        return get_object_or_404(UserVariant, variant__pk=pk, user=user)

    def get_task_object(
        self, task_pk: str, variant_pk: str, user: User
    ) -> UserVariantTask:
        return get_object_or_404(
            UserVariantTask,
            variant__variant__pk=variant_pk,
            task__pk=task_pk,
            variant__user=user,
        )

    def post(self, request, pk: str, task_pk: str):
        variant = self.get_variant_object(pk, request.user)

        if not variant.is_started:
            return Response(
                {"detail": "Variant is not started."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if variant.is_completed:
            return Response(
                {"detail": "Variant completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = self.get_task_object(task_pk=task_pk, variant_pk=pk, user=request.user)
        serializer = AnswerTaskSerializer(data=request.data)
        if serializer.is_valid():
            task.try_answer(serializer.validated_data["answer"])
            return Response(
                UserVariantSerializer(variant, context={"request": request}).data
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SkipVariantTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get_variant_object(self, pk: str, user: User) -> UserVariant:
        return get_object_or_404(UserVariant, variant__pk=pk, user=user)

    def get_task_object(
        self, task_pk: str, variant_pk: str, user: User
    ) -> UserVariantTask:
        return get_object_or_404(
            UserVariantTask,
            variant__variant__pk=variant_pk,
            task__pk=task_pk,
            variant__user=user,
        )

    def post(self, request, pk: str, task_pk: str):
        variant = self.get_variant_object(pk, request.user)

        if not variant.is_started:
            return Response(
                {"detail": "Variant is not started."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if variant.is_completed:
            return Response(
                {"detail": "Variant completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = self.get_task_object(task_pk=task_pk, variant_pk=pk, user=request.user)
        task.try_skip()
        return Response(
            UserVariantSerializer(variant, context={"request": request}).data
        )
