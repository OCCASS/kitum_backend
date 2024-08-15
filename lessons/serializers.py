from rest_framework.serializers import (
    CharField,
    JSONField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    DateField,
    URLField,
    ListSerializer
)

from tasks.serializers import UserTaskSerializer
from .models import *


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class CreateLessonSerializer(Serializer):
    title = CharField()
    opens_at = DateField()
    video_url = URLField()
    subscriptions = ListSerializer(child=CharField())

    def save(self, **kwargs):
        print(self.validated_data)
        subscriptions_ids = self.validated_data["subscriptions"]
        subscriptions = Subscription.objects.filter(id__in=subscriptions_ids)
        lesson = Lesson(
            title=self.validated_data["title"],
            opens_at=self.validated_data["opens_at"],
            video_url=self.validated_data["video_url"],
        )
        lesson.save()
        lesson.subscriptions.add(*subscriptions)
        lesson.save()


class UserLessonSerializer(ModelSerializer):
    id = SerializerMethodField()
    title = CharField()
    content = CharField()
    tasks = SerializerMethodField()
    opens_at = SerializerMethodField()
    video_url = SerializerMethodField()

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
            "video_url"
        )

    def get_id(self, obj: UserLesson) -> str:
        return obj.lesson.id

    def get_opens_at(self, obj: UserLesson):
        return obj.lesson.opens_at

    def get_tasks(self, obj: UserLesson):
        if self._should_hide_tasks(obj):
            return []
        return self._serialized_tasks(obj)

    def get_video_url(self, obj: UserLesson):
        return obj.lesson.video_url

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
