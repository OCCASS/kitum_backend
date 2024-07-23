from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import BaseModel
from .exceptions import TaskAlreadyAnswered, TaskAlreadySkipped
from .managers import UserTaskManager

User = get_user_model()


class Task(BaseModel):
    """Задача из ЕГЭ"""

    ANY = "A"
    TABLE = "T"
    TYPE_CHOICES = {ANY: "Any", TABLE: "Table"}
    TABLE_TYPE_KIM_NUMBERS = (17, 18, 20, 25, 26, 27)

    class Meta:
        db_table = "task"
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    kim_number = models.IntegerField()
    cost = models.IntegerField()
    content = models.TextField()
    correct_answer = models.JSONField(null=False)
    complexity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=ANY)

    def save(self, *args, **kwargs):
        if self.kim_number in self.TABLE_TYPE_KIM_NUMBERS:
            self.type = self.TABLE
        super().save(*args, **kwargs)


class TaskFile(BaseModel):
    """Файл задачи"""

    class Meta:
        db_table = "task_file"

    name = models.CharField(max_length=255, blank=False)
    file = models.FileField(upload_to="files")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="files")


class UserTask(BaseModel):
    """Задача пользователя, которая доступна ему"""

    class Meta:
        db_table = "user_task"
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    answer = models.JSONField(null=True)
    is_correct = models.BooleanField(null=True, default=None)
    is_skipped = models.BooleanField(default=False)

    objects = UserTaskManager()

    def try_answer(self, answer: list) -> None:
        self.answer = answer
        self.is_correct = self.task.correct_answer == answer
        self.is_skipped = False
        self.save()

    def try_skip(self) -> None:
        if self.is_skipped:
            raise TaskAlreadySkipped
        elif self.answer is not None:
            raise TaskAlreadyAnswered

        self.is_skipped = True
        self.save()
