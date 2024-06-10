from django.contrib.auth import get_user_model
from django.db import models

from core.models import BaseModel

User = get_user_model()


class Lesson(BaseModel):
    """Модель урока"""

    class Meta:
        db_table = "lesson"

    title = models.CharField(max_length=255, blank=False)
    content = models.TextField(blank=False)


class Task(BaseModel):
    """Задача из ЕГЭ"""

    class Meta:
        db_table = "task"

    kim_number = models.IntegerField()
    cost = models.IntegerField()
    content = models.TextField()
    answer = models.CharField(max_length=255)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="tasks")


class TaskFile(BaseModel):
    """Файл задачи"""

    class Meta:
        db_table = "task_file"

    file = models.FileField(upload_to="files")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="files")


class UserLesson(BaseModel):
    """Урок пользователя, который доступен ему"""

    class Meta:
        db_table = "user_lesson"

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lessons")
    is_closed = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    is_skipped = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)


class UserTask(BaseModel):
    """Задача пользователя, которая доступна ему"""

    class Meta:
        db_table = "user_task"

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    lesson = models.ForeignKey(
        UserLesson, on_delete=models.CASCADE, related_name="tasks"
    )
    answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(null=True, default=None)
    is_skipped = models.BooleanField(default=False)
