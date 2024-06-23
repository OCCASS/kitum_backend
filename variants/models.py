from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from lessons.exceptions import TaskAlreadyAnswered, TaskAlreadySkipped
from lessons.models import Task

from .exceptions import VariantAlreadyCompleted, VariantAlreadyStarted

User = get_user_model()


class Variant(BaseModel):
    class Meta:
        db_table = "variant"

    title = models.CharField(max_length=255, blank=False)
    tasks = models.ManyToManyField(Task)


class UserVariant(BaseModel):
    class Meta:
        db_table = "user_variant"

    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)

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
        self.save()

    @property
    def is_completed(self):
        return bool(self.completed_at)


class UserVariantTask(BaseModel):
    class Meta:
        db_table = "user_variant_task"

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    variant = models.ForeignKey(
        UserVariant, on_delete=models.CASCADE, related_name="tasks"
    )
    answer = models.CharField(max_length=255, null=True)
    is_correct = models.BooleanField(null=True, default=None)
    is_skipped = models.BooleanField(default=False)

    def try_answer(self, answer: str) -> None:
        self.answer = answer
        self.is_correct = self.task.correct_answer == answer
        self.save()

    def try_skip(self) -> None:
        if self.is_skipped:
            raise TaskAlreadySkipped
        elif self.answer != None:
            raise TaskAlreadyAnswered

        self.is_skipped = True
        self.save()
