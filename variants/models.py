from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from lessons.exceptions import TaskAlreadyAnswered, TaskAlreadySkipped
from lessons.models import Task

from .exceptions import VariantAlreadyCompleted, VariantAlreadyStarted
from .managers import UserVariantManager

User = get_user_model()


class Variant(BaseModel):
    class Meta:
        db_table = "variant"
        verbose_name = "Вариант"
        verbose_name_plural = "Варианты"

    title = models.CharField(max_length=255, blank=False)
    tasks = models.ManyToManyField(Task)


class UserVariant(BaseModel):
    class Meta:
        db_table = "user_variant"
        ordering = (
            "-completed_at",
            "started_at",
        )
        verbose_name = "Вариант"
        verbose_name_plural = "Варианты"

    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    tasks = models.ManyToManyField("UserVariantTask")

    objects = UserVariantManager()

    def start(self):
        if self.started_at:
            raise VariantAlreadyStarted

        self.started_at = timezone.now()
        self.save()

    @property
    def is_started(self):
        return bool(self.started_at)

    def complete(self):
        if self.completed_at:
            raise VariantAlreadyCompleted

        self.completed_at = timezone.now()
        self.tasks.filter(answer=None).update(is_skipped=True)
        self.save()

    @property
    def is_completed(self):
        return bool(self.completed_at)


class UserVariantTask(BaseModel):
    class Meta:
        db_table = "user_variant_task"
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    answer = models.JSONField(null=True)
    is_correct = models.BooleanField(null=True, default=None)
    is_skipped = models.BooleanField(default=False)

    def try_answer(self, answer: list) -> None:
        self.answer = answer
        self.is_correct = self.task.correct_answer == answer
        self.save()

    def try_skip(self) -> None:
        if self.is_skipped:
            raise TaskAlreadySkipped
        elif self.answer is not None:
            raise TaskAlreadyAnswered

        self.is_skipped = True
        self.save()


class GeneratedUserVariant(BaseModel):
    class Meta:
        db_table = "generated_user_variant"
        verbose_name = "Сгенерированный вариант"
        verbose_name_plural = "Сгенерированные варианты"

    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tasks = models.ManyToManyField(UserVariantTask)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
