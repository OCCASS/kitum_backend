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
    TYPE_CHOICES = {ANY: "Текст", FILE: "Файл"}

    class Meta:
        db_table = "task"
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    name = models.CharField(
        "Название",
        max_length=255,
        help_text="Название задачи не будет нигде отображаться. Оно служит лишь для удобства поиска и выбора задач.",
    )
    content = models.TextField(
        "Содержание",
        help_text="Текст в формате Markdown. Также текст поддерживает синтаксис LaTeX.",
    )
    correct_answer = models.CharField(
        "Правильный ответ",
        blank=True,
        null=True,
        help_text="Если тип ответа на задачу: Файл, то указывать не нужно.",
    )
    type = models.CharField(
        "Тип ответа на задание", max_length=1, choices=TYPE_CHOICES, default=ANY
    )

    def clean(self):
        if self.type != self.FILE and self.correct_answer is None:
            raise ValueError(
                f'Task with type "{self.TYPE_CHOICES.get(self.type)}" should have correct_answer'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name)


class TaskFile(BaseModel):
    """Файл задачи"""

    class Meta:
        db_table = "task_file"
        verbose_name = "Файл задачи"
        verbose_name_plural = "Файлы задач"

    name = models.CharField("Название", max_length=255, blank=False)
    file = models.FileField("Файл", upload_to="files")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="files")


class UserTask(BaseModel):
    """Задача пользователя, которая доступна ему"""

    class Meta:
        db_table = "user_task"
        verbose_name = "Задача пользователя"
        verbose_name_plural = "Задачи пользователя"

    task = models.ForeignKey(Task, verbose_name="Задача", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, verbose_name="Пользователь", on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(
        "lessons.UserLesson",
        verbose_name="Урок",
        on_delete=models.SET_NULL,
        null=True,
        related_name="tasks",
    )
    answer = models.CharField("Ответ", null=True, blank=True)
    answer_file = models.FileField(
        "Файл ответа", upload_to="user_task_answers/", null=True, blank=True
    )
    is_correct = models.BooleanField("Верно", null=True, default=None)
    is_skipped = models.BooleanField("Пропущен", default=False)

    objects = UserTaskManager()

    def try_answer(self, answer: str | UploadedFile) -> None:
        self.is_skipped = False

        if isinstance(answer, str):
            self.answer = answer
            self.answer_file = None
        elif isinstance(answer, UploadedFile):
            self.answer_file = answer
            self.answer = None
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
        return str(self.task.name)
