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
    kinescope_video_id = models.CharField(max_length=64, blank=False, null=False)
    tasks = models.ManyToManyField(Task)
    opens_at = models.DateField()
    subscriptions = models.ManyToManyField(Subscription)


class UserLesson(BaseModel):
    """Урок пользователя, который доступен ему"""

    NOT_STARTED = "not_started"
    STARTED = "started"
    COMPLETED = "completed"
    TASKS_COMPLETED = "tasks_completed"
    STATUS_CHOICES = {0: NOT_STARTED, 1: STARTED, 2: COMPLETED,
                      3: TASKS_COMPLETED}

    class Meta:
        db_table = "user_lesson"
        ordering = (
            "lesson__opens_at",
            "status",
            "created_at",
        )
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lessons")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=NOT_STARTED)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    complete_tasks_deadline = models.DateTimeField()
    result = models.IntegerField(null=True)
    tasks = models.ManyToManyField(UserTask)

    objects = UserLessonManager()

    def save(self, *args, **kwargs):
        self.complete_tasks_deadline = self.complete_tasks_deadline.replace(hour=23, minute=59, second=59,
                                                                            microsecond=0)
        super().save(*args, **kwargs)

    @property
    def is_closed(self):
        return self.lesson.opens_at > timezone.localdate()

    @property
    def is_completed(self):
        return self.status == self.COMPLETED

    def try_complete(self) -> None:
        if self.is_closed:
            raise LessonClosed
        elif self.is_completed:
            raise LessonAlreadyCompleted

        self.status = self.COMPLETED
        self.completed_at = timezone.now()
        self.save()

    def try_complete_tasks(self) -> None:
        if self.is_closed:
            raise LessonClosed
        elif self.status == self.TASKS_COMPLETED:
            raise LessonTasksAlreadyCompleted

        self.status = self.TASKS_COMPLETED
        self.tasks.filter(answer=None).update(is_skipped=True)
        self.result = self._get_result()
        self.save()

    def _get_result(self) -> int:
        """Процент от правильно выполненных задач"""

        total_count = self.tasks.all().count()
        correct_count = self.tasks.filter(is_correct=True).count()
        return math.ceil(correct_count / total_count * 100)
