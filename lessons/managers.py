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
            opens_at__lte=user_subscription.active_before
        ).values("id")
        return self.filter(lesson__id__in=models.Subquery(lessons_subquery))

    def available_for(self, pk: str, user: User):
        """Возвращает урок, который были куплен пользователем, то есть доступный ему"""

        user_subscription = self._get_active_user_subscription(user)
        if not user_subscription:
            return self.none()

        return self.filter(
            lesson__pk=pk, lesson__opens_at__lte=user_subscription.active_before
        ).first()

    def _get_active_user_subscription(self, user: User) -> UserSubscription | None:
        return (
            UserSubscription.objects.filter(
                user=user, active_before__gte=timezone.now()
            )
            .select_related("subscription")
            .first()
        )


class UserLessonManager(models.Manager):
    def get_queryset(self):
        return (
            UserLessonQuerySet(self.model, using=self._db)
            .select_related("lesson")
            .annotate(
                title=models.F("lesson__title"), content=models.F("lesson__content")
            )
        )

    def all_available_for(self, user: User):
        return self.get_queryset().all_available_for(user)

    def available_for_or_404(self, pk: str, user: User):
        obj = self.get_queryset().available_for(pk, user)
        if not obj:
            raise Http404
        return obj
