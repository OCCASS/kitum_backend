from typing import cast

from django.contrib.auth import get_user_model
from django.db import models
from django.http import Http404

User = get_user_model()


class UserLessonQuerySet(models.QuerySet):
    def all_available_for(self, user: User):
        """Возвращает уроки, которые были куплены пользователем, то есть доступные ему"""
        return self.filter(opens_at__lte=timezone.now(), user=user)

    def available_for(self, pk: str, user: User):
        """Возвращает урок, который были куплен пользователем, то есть доступный ему"""

        return self.filter(
            lesson__pk=pk, opens_at__lte=timezone.now(), user=user
        ).first()


class UserLessonManager(models.Manager):
    def get_queryset(self) -> UserLessonQuerySet:
        return cast(
            UserLessonQuerySet,
            UserLessonQuerySet(self.model, using=self._db)
            .select_related("lesson")
            .annotate(
                title=models.F("lesson__title"), content=models.F("lesson__content")
            ),
        )

    def all_available_for(self, user: User):
        return self.get_queryset().all_available_for(user)

    def available_for_or_404(self, pk: str, user: User):
        obj = self.get_queryset().available_for(pk, user)
        if not obj:
            raise Http404
        return obj


class UserLessonTaskManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("task")
            .annotate(
                kim_number=models.F("task__kim_number"),
                cost=models.F("task__cost"),
                content=models.F("task__content"),
                type=models.F("task__type"),
            )
        )
