from rest_framework.serializers import CharField
from rest_framework.serializers import FileField
from rest_framework.serializers import JSONField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer
from rest_framework.serializers import SerializerMethodField
from rest_framework.serializers import ValidationError

from .models import *
from subscriptions.serializers import SubscriptionSerializer
from tasks.serializers import UserTaskSerializer
from user.serializers import UserSerializer


class LessonFileSerializer(ModelSerializer):
    file = SerializerMethodField()

    class Meta:
        model = LessonFile
        fields = (
            "name",
            "file",
        )

    def get_file(self, obj: LessonFile):
        request = self.context.get("request")
        file_url = obj.file.url
        return request.build_absolute_uri(file_url)


class UserLessonSerializer(ModelSerializer):
    id = SerializerMethodField()
    title = CharField()
    content = CharField()
    files = SerializerMethodField()
    tasks = SerializerMethodField()
    opens_at = SerializerMethodField()
    kinescope_video_id = SerializerMethodField()
    author = SerializerMethodField()
    subscription = SerializerMethodField()

    class Meta:
        model = UserLesson
        fields = (
            "id",
            "title",
            "content",
            "files",
            "tasks",
            "is_closed",
            "status",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
            "complete_tasks_deadline",
            "opens_at",
            "kinescope_video_id",
            "author",
            "subscription",
        )

    def get_id(self, obj: UserLesson) -> str:
        return obj.lesson.id

    def get_opens_at(self, obj: UserLesson):
        return obj.lesson.opens_at

    def get_tasks(self, obj: UserLesson):
        if self._should_hide_tasks(obj):
            return []
        return self._serialized_tasks(obj)

    def get_files(self, obj: UserLesson):
        return LessonFileSerializer(
            obj.lesson.files, many=True, read_only=True, context=self.context
        ).data

    def get_kinescope_video_id(self, obj: UserLesson):
        return obj.lesson.kinescope_video_id

    def get_author(self, obj: UserLesson):
        author = obj.lesson.author
        if author:
            return UserSerializer(author).data
        return None

    def get_subscription(self, obj: UserLesson):
        return SubscriptionSerializer(obj.lesson.subscription).data

    def to_representation(self, instance: UserLesson):
        # remove tasks, if lesson not completed
        if self._should_hide_tasks(instance):
            self.fields.pop("tasks", None)

        data = super().to_representation(instance)
        if "tasks" in data:
            data["tasks"] = sorted(data["tasks"], key=lambda task: task["created_at"])
        return data

    def _should_hide_tasks(self, obj: UserLesson):
        return (
            obj.status != UserLesson.COMPLETED
            and obj.status != UserLesson.TASKS_COMPLETED
        ) or self.context.get("without_tasks", False)

    def _serialized_tasks(self, obj: UserLesson):
        tasks = (
            obj.tasks.prefetch_related("task", "task__files")
            .all()
            .order_by("created_at")
        )
        context = self.context
        context.update(
            {"show_correct_answer": obj.status == UserLesson.TASKS_COMPLETED}
        )
        serializer = UserTaskSerializer(
            tasks, many=True, read_only=True, context=context
        )
        return serializer.data


class AnswerTaskSerializer(Serializer):
    answer = JSONField(required=False)
    answer_file = FileField(required=False)

    def validate(self, attrs):
        answer = attrs.get("answer")
        answer_file = attrs.get("answer_file")

        if not answer and not answer_file:
            raise ValidationError("You must provide either 'answer' or 'answer_file'.")
        if answer and answer_file:
            raise ValidationError(
                "Only one of 'answer' or 'answer_file' can be provided."
            )
        return attrs
