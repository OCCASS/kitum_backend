from rest_framework.serializers import (
    CharField,
    IntegerField,
    JSONField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
)

from lessons.serializers import TaskFileSerializer
from .models import *


class UserVariantTaskSerializer(ModelSerializer):
    id = SerializerMethodField()
    kim_number = SerializerMethodField()
    cost = SerializerMethodField()
    content = SerializerMethodField()
    type = SerializerMethodField()
    files = SerializerMethodField()

    class Meta:
        model = UserVariantTask
        fields = (
            "id",
            "kim_number",
            "cost",
            "content",
            "answer",
            "type",
            "is_correct",
            "is_skipped",
            "created_at",
            "files",
        )

    def get_id(self, obj: UserVariantTask):
        return obj.task.id

    def get_kim_number(self, obj: UserVariantTask):
        return obj.task.kim_number

    def get_cost(self, obj: UserVariantTask):
        return obj.task.cost

    def get_type(self, obj: UserVariantTask):
        return obj.task.type

    def get_content(self, obj: UserVariantTask):
        return obj.task.content

    def get_files(self, obj: UserVariantTask):
        files = obj.task.files.all()
        serializer = TaskFileSerializer(files, many=True, context=self.context)
        return serializer.data


class UserVariantSerializer(ModelSerializer):
    id = SerializerMethodField()
    title = SerializerMethodField()
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

    def get_id(self, obj: UserVariant) -> str:
        return obj.variant.id

    def get_title(self, obj: UserVariant) -> str:
        return obj.variant.title

    def get_tasks(self, obj: UserVariant):
        tasks = (
            obj.tasks.prefetch_related("task", "task__files")
            .all()
            .order_by("task__kim_number")
        )
        serializer = UserVariantTaskSerializer(
            tasks, many=True, read_only=True, context=self.context
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


class GeneratedVariantSerializer(ModelSerializer):
    tasks = SerializerMethodField()

    class Meta:
        model = GeneratedUserVariant
        fields = "__all__"

    def get_tasks(self, obj: UserVariant):
        tasks = (
            obj.tasks.prefetch_related("task", "task__files")
            .all()
            .order_by("task__kim_number")
        )
        serializer = UserVariantTaskSerializer(
            tasks, many=True, read_only=True, context=self.context
        )
        return serializer.data
