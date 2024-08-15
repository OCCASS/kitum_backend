from rest_framework.serializers import (
    CharField,
    IntegerField,
    JSONField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
)

from tasks.serializers import UserTaskSerializer
from .models import *


class VariantSerializer(ModelSerializer):
    class Meta:
        model = Variant
        fields = "__all__"


class UserVariantSerializer(ModelSerializer):
    tasks = SerializerMethodField()

    class Meta:
        model = UserVariant
        fields = (
            "id",
            "title",
            "tasks",
            "started_at",
            "completed_at",
            "is_completed",
            "is_started",
            "created_at",
            "status",
            "result"
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if "tasks" in data:
            is_not_completed = not instance.is_completed
            data["tasks"] = self.prepare_tasks(
                data["tasks"], hide_correctness=is_not_completed
            )
        return data

    def prepare_tasks(self, tasks: list, *, hide_correctness: bool) -> list:
        if hide_correctness:
            tasks = self.hide_tasks_correctness(tasks)
        return sorted(tasks, key=lambda task: task["kim_number"])

    def hide_tasks_correctness(self, tasks: list) -> list:
        for i in range(len(tasks)):
            tasks[i]["is_correct"] = None
        return tasks

    def get_tasks(self, obj: UserVariant):
        tasks = (
            obj.tasks.prefetch_related("task", "task__files")
            .all()
            .order_by("task__kim_number")
        )
        context = self.context.copy()
        context.update({"show_correct_answer": obj.is_completed})
        serializer = UserTaskSerializer(
            tasks, many=True, read_only=True, context=context
        )
        return serializer.data


class UserVariantWithoutTasksSerializer(UserVariantSerializer):
    def to_representation(self, instance):
        self.fields.pop("tasks", None)
        return super().to_representation(instance)


class AnswerTaskSerializer(Serializer):
    answer = JSONField(required=True)


class GenerateVariantSerializer(Serializer):
    name = CharField(required=True)
    complexity = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])
