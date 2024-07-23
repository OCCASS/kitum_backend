from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from tasks.models import Task, UserTask
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


class VariantScoreTable(models.Model):
    class Meta:
        db_table = "variant_score_table"
        verbose_name = "Таблица первичных и вторичных баллов"
        verbose_name_plural = "Таблицы первичных и вторичных баллов"

    id = models.AutoField(primary_key=True)
    primary = models.IntegerField()
    secondary = models.IntegerField()


class UserVariant(BaseModel):
    NOT_STARTED = "not_started"
    STARTED = "started"
    COMPLETED = "completed"
    STATUS_CHOICES = {NOT_STARTED: NOT_STARTED, STARTED: STARTED, COMPLETED: COMPLETED}

    class Meta:
        db_table = "user_variant"
        ordering = (
            "-completed_at",
            "started_at",
        )
        verbose_name = "Вариант"
        verbose_name_plural = "Варианты"

    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=NOT_STARTED)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    tasks = models.ManyToManyField(UserTask)
    generated = models.BooleanField(default=False)
    complexity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    result = models.IntegerField(default=None, null=True)

    objects = UserVariantManager()

    def start(self):
        if self.started_at:
            raise VariantAlreadyStarted

        self.started_at = timezone.now()
        self.status = self.STARTED
        self.save()

    def complete(self):
        if self.completed_at:
            raise VariantAlreadyCompleted

        self.completed_at = timezone.now()
        self.status = self.COMPLETED
        self.tasks.filter(answer=None).update(is_skipped=True)
        self.result = self._get_result()
        self.save()

    @property
    def is_started(self):
        return self.status == self.STARTED

    @property
    def is_completed(self):
        return self.status == self.COMPLETED

    def _get_result(self) -> int:
        try:
            total_primary_score = self.tasks. \
                filter(is_correct=True). \
                aggregate(total_cost=models.Sum("cost"))["total_cost"]
            return VariantScoreTable.objects.get(primary=total_primary_score).secondary
        except models.ObjectDoesNotExist:
            return 0
