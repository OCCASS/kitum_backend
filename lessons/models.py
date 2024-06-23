from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from core.models import BaseModel

from .exceptions import *

User = get_user_model()


class Task(BaseModel):
    """Задача из ЕГЭ"""

    class Meta:
        db_table = "task"

    kim_number = models.IntegerField()
    cost = models.IntegerField()
    content = models.TextField()
    correct_answer = models.CharField(max_length=255, null=True)


class Lesson(BaseModel):
    """Модель урока"""

    class Meta:
        db_table = "lesson"

    title = models.CharField(max_length=255, blank=False)
    content = models.TextField(blank=False)
    tasks = models.ManyToManyField(Task)


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

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lessons")
    is_closed = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    is_skipped = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    complete_tasks_deadline = models.DateTimeField(null=False)
    is_tasks_completed = models.BooleanField(default=False)

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
