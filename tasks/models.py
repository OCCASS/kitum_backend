from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from django.db import models

from core.models import BaseModel
from tasks.exceptions import TaskAlreadyAnswered
from tasks.exceptions import TaskAlreadySkipped
from tasks.managers import UserTaskManager

User = get_user_model()


class Task(BaseModel):
    """Задача из ЕГЭ"""

    ANY = "A"
    FILE = "F"
    TYPE_CHOICES = {ANY: "Any", FILE: "File"}

    class Meta:
        db_table = "task"
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    content = models.TextField()
    correct_answer = models.CharField(blank=True, null=True)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=ANY)

    def clean(self):
        if self.type != self.FILE and self.correct_answer is None:
            raise ValueError(
                f'Task with type "{self.TYPE_CHOICES.get(self.type)}" should have correct_answer'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.content)


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
        verbose_name = "Задача пользователя"
        verbose_name_plural = "Задачи пользователя"

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    answer = models.CharField(null=True, blank=True)
    answer_file = models.FileField(
        upload_to="user_task_answers/", null=True, blank=True
    )
    is_correct = models.BooleanField(null=True, default=None)
    is_skipped = models.BooleanField(default=False)

    objects = UserTaskManager()

    def try_answer(self, answer: str | UploadedFile) -> None:
        self.is_skipped = False

        if isinstance(answer, str):
            self.answer = answer
            self.answer_file = None
            self.is_correct = self.correct_answer == answer
        elif isinstance(answer, UploadedFile):
            self.answer_file = answer
            self.answer = None
            self.is_correct = None
        else:
            raise ValueError("Unsupported answer type")

        self.save()

    def try_skip(self) -> None:
        if self.is_skipped:
            raise TaskAlreadySkipped
        elif self.answer is not None:
            raise TaskAlreadyAnswered

        self.is_skipped = True
        self.save()

    def __str__(self):
        return str(self.task.content)
