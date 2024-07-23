import math

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from subscriptions.models import Subscription
from tasks.models import Task, UserTask
from .exceptions import *
from .managers import UserLessonManager

User = get_user_model()


class Lesson(BaseModel):
    """Модель урока"""

    class Meta:
        db_table = "lesson"
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    title = models.CharField(max_length=255, blank=False)
    content = models.TextField(blank=False)
    tasks = models.ManyToManyField(Task)
    subscriptions = models.ManyToManyField(Subscription)


class UserLesson(BaseModel):
    """Урок пользователя, который доступен ему"""

    class Meta:
        db_table = "user_lesson"
        ordering = (
            "opens_at",
            "is_tasks_completed",
            "-is_completed",
            "created_at",
        )
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lessons")
    is_completed = models.BooleanField(default=False)
    is_skipped = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    complete_tasks_deadline = models.DateTimeField(null=False)
    is_tasks_completed = models.BooleanField(default=False)
    result = models.IntegerField(null=True)
    opens_at = models.DateTimeField(null=False)
    tasks = models.ManyToManyField(UserTask)

    objects = UserLessonManager()

    @property
    def is_closed(self):
        return self.opens_at > timezone.now()

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
        self.tasks.filter(answer=None).update(is_skipped=True)
        self.result = self._get_result()
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

    def _get_result(self) -> int:
        """Процент от правильно выполненных задач"""

        total_count = self.tasks.all().count()
        correct_count = self.tasks.filter(is_correct=True).count()
        return math.ceil(correct_count / total_count * 100)
