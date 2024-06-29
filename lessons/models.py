from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from lessons.managers import UserLessonManager
from subscribtions.models import Subscribtion

from .exceptions import *

User = get_user_model()


class Task(BaseModel):
    """Задача из ЕГЭ"""

    ANY = "A"
    TABLE = "T"
    TYPE_CHOICES = {ANY: "Any", TABLE: "Table"}
    TABLE_TYPE_KIM_NUMBERS = (17, 18, 20, 25, 26, 27)

    class Meta:
        db_table = "task"

    kim_number = models.IntegerField()
    cost = models.IntegerField()
    content = models.TextField()
    correct_answer = models.JSONField(null=False)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=ANY)

    def save(self, *args, **kwargs):
        if self.kim_number in self.TABLE_TYPE_KIM_NUMBERS:
            self.type = self.TABLE
        super().save(*args, **kwargs)


class Lesson(BaseModel):
    """Модель урока"""

    class Meta:
        db_table = "lesson"

    title = models.CharField(max_length=255, blank=False)
    content = models.TextField(blank=False)
    tasks = models.ManyToManyField(Task)
    subscribtion = models.ForeignKey(
        Subscribtion, on_delete=models.SET_NULL, related_name="lessons", null=True
    )


class TaskFile(BaseModel):
    """Файл задачи"""

    class Meta:
        db_table = "task_file"

    name = models.CharField(max_length=255, blank=False)
    file = models.FileField(upload_to="files")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="files")


class UserLesson(BaseModel):
    """Урок пользователя, который доступен ему"""

    class Meta:
        db_table = "user_lesson"
        ordering = (
            "is_closed",
            "is_tasks_completed",
            "-is_completed",
            "created_at",
        )

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lessons")
    is_closed = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    is_skipped = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    complete_tasks_deadline = models.DateTimeField(null=False)
    is_tasks_completed = models.BooleanField(default=False)

    objects = UserLessonManager()

    def try_complete(self) -> None:
        if self.is_closed:
            raise LessonClosed
        elif self.is_skipped:
            raise LessonAlreadySkipped
        elif self.is_completed:
            raise LessonAlreadyCompleted

        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()

    def try_complete_tasks(self) -> None:
        if self.is_closed:
            raise LessonClosed
        elif self.is_tasks_completed:
            raise LessonTasksAlreadyCompleted

        self.is_tasks_completed = True

        for task in self.tasks.all():
            if not task.answer:
                task.is_skipped = True
                task.save()

        self.save()

    def try_skip(self) -> None:
        if self.is_closed:
            raise LessonClosed
        elif self.is_skipped:
            raise LessonAlreadySkipped
        elif self.is_completed:
            raise LessonAlreadyCompleted

        self.is_skipped = True
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()


class UserLessonTask(BaseModel):
    """Задача пользователя, которая доступна ему"""

    class Meta:
        db_table = "user_lesson_task"

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    lesson = models.ForeignKey(
        UserLesson, on_delete=models.CASCADE, related_name="tasks"
    )
    answer = models.JSONField(null=True)
    is_correct = models.BooleanField(null=True, default=None)
    is_skipped = models.BooleanField(default=False)

    def try_answer(self, answer: list) -> None:
        self.answer = answer
        self.is_correct = self.task.correct_answer == answer
        self.is_skipped = False
        self.save()

    def try_skip(self) -> None:
        if self.is_skipped:
            raise TaskAlreadySkipped
        elif self.answer != None:
            raise TaskAlreadyAnswered

        self.is_skipped = True
        self.save()
