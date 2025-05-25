from django.contrib import admin

from .models import Lesson
from .models import LessonFile
from .models import UserLesson


class LessonFileInline(admin.TabularInline):
    model = LessonFile
    extra = 0
    fields = ("name", "file")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "opens_at", "subscription")
    fields = (
        "title",
        "author",
        "kinescope_video_id",
        "content",
        "tasks",
        "subscription",
        "opens_at",
    )
    inlines = [LessonFileInline]
    filter_horizontal = ("tasks",)


@admin.register(UserLesson)
class UserLessonAdmin(admin.ModelAdmin):
    list_display = ("id", "lesson", "user")
    filter_horizontal = ("tasks",)
