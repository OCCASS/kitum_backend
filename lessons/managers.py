from typing import cast

from django.contrib.auth import get_user_model
from django.db import models
from django.http import Http404
from django.utils import timezone
from subscriptions.models import UserSubscription

User = get_user_model()


class UserLessonQuerySet(models.QuerySet):
    def all_available_for(self, user: User):
        """Возвращает уроки, которые были куплены пользователем, то есть доступные ему"""

        user_subscription = self._get_active_user_subscription(user)
        if not user_subscription:
            return self.none()

        lessons_subquery = user_subscription.subscription.lessons.filter(
            opens_at__lte=user_subscription.active_before,
        ).values("id")

        # Получить откртые уроки у которых зависимый урок (если он есть) тоже открыт,
        # а также время откртыия урока до окончания подписки
        lessons_are_open = models.Q(is_closed=False)
        lessons_within_subscription_period = models.Q(
            lesson__id__in=models.Subquery(lessons_subquery)
        )
        lessons_are_accessible = models.Q(
            lesson__depends_on__userlesson__is_closed=False,
            lesson__depends_on__userlesson__is_tasks_completed=True,
        ) | models.Q(lesson__depends_on__isnull=True)
        query = (
            lessons_are_open
            & lessons_within_subscription_period
            & lessons_are_accessible
        )
        return self.filter(query)

    def available_for(self, pk: str, user: User):
        """Возвращает урок, который были куплен пользователем, то есть доступный ему"""

        user_subscription = self._get_active_user_subscription(user)
        if not user_subscription:
            return self.none()

        # Получить откртый урок у которого зависимый урок (если он есть) тоже открыт,
        # а также время откртия урока до окончания подписки
        lesson_is_open = models.Q(is_closed=False)
        lesson_opens_before_subscription_end = models.Q(
            lesson__opens_at__lte=user_subscription.active_before
        )
        lesson_is_accessible = models.Q(
            lesson__depends_on__userlesson__is_closed=False,
            lesson__depends_on__userlesson__is_tasks_completed=True,
        ) | models.Q(lesson__depends_on__isnull=True)
        lesson_with_pk = models.Q(lesson__pk=pk)
        query = (
            lesson_with_pk
            & lesson_is_open
            & lesson_opens_before_subscription_end
            & lesson_is_accessible
        )
        return self.filter(query).first()

    def _get_active_user_subscription(self, user: User) -> UserSubscription | None:
        """Получить текущую подписку пользователя, если ее нет, то возвращается `None`"""

        return (
            UserSubscription.objects.filter(
                user=user, active_before__gte=timezone.now()
            )
            .select_related("subscription")
            .first()
        )


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
