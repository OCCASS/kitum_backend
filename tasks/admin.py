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
    list_display = ("id", "type")
    inlines = [TaskFileInline]


@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "task")
