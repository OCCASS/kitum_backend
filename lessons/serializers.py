from rest_framework.serializers import (
    CharField,
    JSONField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
)

from .models import *


class TaskFileSerializer(ModelSerializer):
    file = SerializerMethodField()

    class Meta:
        model = TaskFile
        fields = (
            "name",
            "file",
        )

    def get_file(self, obj: TaskFile):
        request = self.context.get("request")
        file_url = obj.file.url
        return request.build_absolute_uri(file_url)


class UserLessonTaskSerializer(ModelSerializer):
    id = SerializerMethodField()
    kim_number = SerializerMethodField()
    cost = SerializerMethodField()
    content = SerializerMethodField()
    type = SerializerMethodField()
    files = SerializerMethodField()

    class Meta:
        model = UserLessonTask
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

    def get_id(self, obj: UserLessonTask):
        return obj.task.id

    def get_kim_number(self, obj: UserLessonTask):
        return obj.task.kim_number

    def get_cost(self, obj: UserLessonTask):
        return obj.task.cost

    def get_content(self, obj: UserLessonTask):
        return obj.task.content

    def get_type(self, obj: UserLessonTask):
        return obj.task.type

    def get_files(self, obj: UserLessonTask):
        files = obj.task.files.all()
        serializer = TaskFileSerializer(files, many=True, context=self.context)
        return serializer.data


class UserLessonSerializer(ModelSerializer):
    id = SerializerMethodField()
    title = CharField()
    content = CharField()
    tasks = SerializerMethodField()

    class Meta:
        model = UserLesson
        fields = (
            "id",
            "title",
            "content",
            "tasks",
            "is_closed",
            "is_completed",
            "is_tasks_completed",
            "is_skipped",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
            "complete_tasks_deadline",
        )

    def get_id(self, obj: UserLesson) -> str:
        return obj.lesson.id

    def get_tasks(self, obj: UserLesson):
        if self._should_hide_tasks(obj):
            return []
        return self._serialized_tasks(obj)

    def to_representation(self, instance: UserLesson):
        # remove tasks, if lesson not completed
        if self._should_hide_tasks(instance):
            self.fields.pop("tasks", None)

        data = super().to_representation(instance)
        if "tasks" in data:
            data["tasks"] = sorted(data["tasks"], key=lambda task: task["created_at"])
        return data

    def _should_hide_tasks(self, obj: UserLesson):
        return (not obj.is_completed and not obj.is_skipped) or self.context.get(
            "without_tasks", False
        )

    def _serialized_tasks(self, obj: UserLesson):
        tasks = (
            obj.tasks.prefetch_related("task", "task__files")
            .all()
            .order_by("created_at")
        )
        serializer = UserLessonTaskSerializer(
            tasks, many=True, read_only=True, context=self.context
        )
        return serializer.data


class AnswerTaskSerializer(Serializer):
    answer = JSONField(required=True)
