from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField

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


class UserTaskSerializer(ModelSerializer):
    kim_number = CharField()
    cost = CharField()
    content = CharField()
    type = CharField()
    files = SerializerMethodField()
    correct_answer = SerializerMethodField()

    class Meta:
        model = UserTask
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
            "correct_answer"
        )

    def get_correct_answer(self, obj: UserTask) -> list | None:
        if self.context.get("show_correct_answer", False):
            return obj.task.correct_answer
        return None

    def get_files(self, obj: UserTask):
        files = obj.task.files.all()
        serializer = TaskFileSerializer(files, many=True, context=self.context)
        return serializer.data
