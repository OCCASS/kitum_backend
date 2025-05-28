from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from lessons.exceptions import *
from lessons.managers import UserLessonManager
from subscriptions.models import Subscription
from subscriptions.models import UserSubscription
from tasks.models import Task

User = get_user_model()


class Lesson(BaseModel):
    """Модель урока"""

    class Meta:
        db_table = "lesson"
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    title = models.CharField("Название", max_length=255, blank=False)
    kinescope_video_id = models.CharField(
        "ID события Kinescope",
        max_length=64,
        blank=True,
        null=True,
        help_text="Идентификатор события в Kinescope. Создается автоматически после создания урока.",
    )
    content = models.TextField("Содержание", blank=False)
    tasks = models.ManyToManyField(Task, verbose_name="Задачи")
    opens_at = models.DateField("Когда открывается")
    subscription = models.ForeignKey(
        Subscription, verbose_name="Подписка", on_delete=models.SET_NULL, null=True
    )
    author = models.ForeignKey(
        User, verbose_name="Автор", on_delete=models.SET_NULL, null=True
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        user_subscriptions = UserSubscription.objects.filter(
            subscription=self.subscription
        )
        for s in user_subscriptions:
            if not UserLesson.objects.filter(lesson=self).exists():
                UserLesson(
                    lesson=self, user=s.user, complete_tasks_deadline=timezone.now()
                ).save()

    def __str__(self):
        return str(self.title)


class LessonFile(BaseModel):
    """Файл задачи"""

    class Meta:
        db_table = "lesson_file"
        verbose_name = "Файл урока"
        verbose_name_plural = "Файлы урока"

    name = models.CharField("Название", max_length=255, blank=False)
    file = models.FileField("Файл", upload_to="files/lessons")
    lesson = models.ForeignKey(
        Lesson, verbose_name="Урок", on_delete=models.CASCADE, related_name="files"
    )


class UserLesson(BaseModel):
    """Урок пользователя, который доступен ему"""

    NOT_STARTED = "not_started"
    STARTED = "started"
    COMPLETED = "completed"
    TASKS_COMPLETED = "tasks_completed"
    STATUS_CHOICES = {
        NOT_STARTED: NOT_STARTED,
        STARTED: STARTED,
        COMPLETED: COMPLETED,
        TASKS_COMPLETED: TASKS_COMPLETED,
    }

    class Meta:
        db_table = "user_lesson"
        ordering = (
            "lesson__opens_at",
            "status",
            "created_at",
        )
        verbose_name = "Урок пользователя"
        verbose_name_plural = "Уроки пользователя"

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lessons")
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default=NOT_STARTED
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    complete_tasks_deadline = models.DateTimeField()
    # tasks = models.ManyToManyField(UserTask)

    objects = UserLessonManager()

    def save(self, *args, **kwargs):
        self.complete_tasks_deadline = self.complete_tasks_deadline.replace(
            hour=23, minute=59, second=59, microsecond=0
        )
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
        self.tasks.filter(answer=None).exclude(type=Task.FILE).update(is_correct=False)
        self.save()

    def __str__(self):
        return f"{self.lesson.title} ({self.user.email})"
