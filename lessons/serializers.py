from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .models import *


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class UserLessonSerializer(ModelSerializer):
    title = SerializerMethodField()
    content = SerializerMethodField()

    class Meta:
        model = UserLesson
        fields = (
            "id",
            "title",
            "content",
            "is_closed",
            "is_completed",
            "is_skipped",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        )

    def get_title(self, obj: UserLesson) -> str:
        return obj.lesson.title

    def get_content(self, obj: UserLesson) -> str:
        return obj.lesson.content
