from django.utils import timezone
from lessons.models import UserLesson
from rest_framework import serializers

from .models import *


class HolidaySerializer(serializers.ModelSerializer):
    """Сериализатор каникул"""

    class Meta:
        model = Holiday
        fields = ("day", "month")


class EventSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    at = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_id(self, obj) -> str:
        raise NotImplemented

    def get_name(self, obj) -> str:
        raise NotImplemented

    def get_at(self, obj) -> timezone.datetime:
        raise NotImplemented

    def get_type(self, obj) -> str:
        raise NotImplemented

    def get_is_available(self, obj) -> bool:
        raise NotImplemented

    def get_is_completed(self, obj) -> bool:
        raise NotImplemented


class LessonEventSerializer(EventSerializer):
    class Meta:
        model = UserLesson
        fields = "__all__"

    def get_id(self, obj: UserLesson):
        return obj.lesson_id

    def get_name(self, obj: UserLesson):
        return obj.title

    def get_at(self, obj: UserLesson):
        return obj.opens_at

    def get_type(self, obj: UserLesson):
        return "lesson"

    def get_is_available(self, obj: UserLesson):
        return obj.opens_at <= timezone.now()

    def get_is_completed(self, obj: UserLesson):
        return obj.is_completed


class HomeworkEventSerializer(EventSerializer):
    class Meta:
        model = UserLesson
        fields = "__all__"

    def get_id(self, obj: UserLesson):
        return obj.lesson_id

    def get_name(self, obj: UserLesson):
        return obj.title

    def get_at(self, obj: UserLesson):
        return obj.complete_tasks_deadline

    def get_type(self, obj: UserLesson):
        return "homework"

    def get_is_available(self, obj: UserLesson):
        return obj.opens_at <= timezone.now()

    def get_is_completed(self, obj: UserLesson):
        return obj.is_tasks_completed
