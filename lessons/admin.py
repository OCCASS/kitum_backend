from django.contrib import admin
from django.utils.html import format_html

from .models import Lesson
from .models import LessonFile
from .models import UserLesson


class LessonFileInline(admin.TabularInline):
    model = LessonFile
    extra = 0
    fields = ("name", "file")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "opens_at",
    )
    fields = (
        "title",
        "author",
        "kinescope_video_id",
        "kinescope_link",
        "content",
        "tasks",
        "subscriptions",
        "opens_at",
    )
    readonly_fields = ("kinescope_link", "kinescope_video_id")
    list_filter = ("author",)
    inlines = [LessonFileInline]
    filter_horizontal = ("tasks", "subscriptions")

    def kinescope_link(self, obj):
        if obj.kinescope_video_id:
            url = f"https://kinescope.io/{obj.kinescope_video_id}"
            return format_html('<a href="{}" target="_blank">{}</a>', url, obj.title)
        return "-"

    kinescope_link.short_description = "Ссылка на событие Kinescope (для админа)"


@admin.register(UserLesson)
class UserLessonAdmin(admin.ModelAdmin):
    list_display = ("id", "lesson", "user")
    # filter_horizontal = ("tasks",)
