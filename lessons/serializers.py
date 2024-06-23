from rest_framework.serializers import (
    CharField,
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
    title = SerializerMethodField()
    content = SerializerMethodField()
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

    def get_title(self, obj: UserLesson) -> str:
        return obj.lesson.title

    def get_content(self, obj: UserLesson) -> str:
        return obj.lesson.content

    def get_tasks(self, obj: UserLesson):
        tasks = obj.tasks.all().order_by("created_at")
        serializer = UserLessonTaskSerializer(
            tasks, many=True, read_only=True, context=self.context
        )
        return serializer.data

    def to_representation(self, instance):
        # remove tasks, if lesson not completed
        if not instance.is_completed and not instance.is_skipped:
            self.fields.pop("tasks", None)

        data = super().to_representation(instance)
        if "tasks" in data:
            data["tasks"] = sorted(data["tasks"], key=lambda task: task["created_at"])
        return data


class AnswerTaskSerializer(Serializer):
    answer = CharField()
