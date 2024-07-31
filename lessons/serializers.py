from rest_framework.serializers import (
    CharField,
    JSONField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
)

from tasks.serializers import UserTaskSerializer
from .models import *


class UserLessonSerializer(ModelSerializer):
    id = SerializerMethodField()
    title = CharField()
    content = CharField()
    tasks = SerializerMethodField()
    opens_at = SerializerMethodField()
    video = SerializerMethodField()

    class Meta:
        model = UserLesson
        fields = (
            "id",
            "title",
            "content",
            "tasks",
            "is_closed",
            "status",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
            "complete_tasks_deadline",
            "opens_at",
            "result",
            "video"
        )

    def get_id(self, obj: UserLesson) -> str:
        return obj.lesson.id

    def get_opens_at(self, obj: UserLesson):
        return obj.lesson.opens_at

    def get_tasks(self, obj: UserLesson):
        if self._should_hide_tasks(obj):
            return []
        return self._serialized_tasks(obj)

    def get_video(self, obj: UserLesson):
        request = self.context.get("request")
        file_url = obj.lesson.video.url
        return request.build_absolute_uri(file_url)

    def to_representation(self, instance: UserLesson):
        # remove tasks, if lesson not completed
        if self._should_hide_tasks(instance):
            self.fields.pop("tasks", None)

        data = super().to_representation(instance)
        if "tasks" in data:
            data["tasks"] = sorted(data["tasks"], key=lambda task: task["created_at"])
        return data

    def _should_hide_tasks(self, obj: UserLesson):
        return (obj.status != UserLesson.COMPLETED and obj.status != UserLesson.TASKS_COMPLETED) or self.context.get(
            "without_tasks", False
        )

    def _serialized_tasks(self, obj: UserLesson):
        tasks = (
            obj.tasks.prefetch_related("task", "task__files")
            .all()
            .order_by("created_at")
        )
        context = self.context
        context.update({"show_correct_answer": obj.status == UserLesson.TASKS_COMPLETED})
        serializer = UserTaskSerializer(
            tasks, many=True, read_only=True, context=context
        )
        return serializer.data


class AnswerTaskSerializer(Serializer):
    answer = JSONField(required=True)
