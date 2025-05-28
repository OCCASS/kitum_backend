from django.contrib import admin

from .models import Task
from .models import TaskFile
from .models import UserTask


class TaskFileInline(admin.TabularInline):
    model = TaskFile
    extra = 0
    fields = (
        "name",
        "file",
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type")
    inlines = [TaskFileInline]


@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ("lesson", "task", "user")
    fields = (
        "lesson",
        "task",
        "user",
        "answer",
        "answer_file",
        "is_correct",
        "is_skipped",
    )
    list_filter = ("lesson", "task", "user")
    # readonly_fields = ("lesson", "task", "user", "answer", "answer_file", "is_skipped")
