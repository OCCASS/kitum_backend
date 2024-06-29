from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from subscribtions.models import UserSubscribtion

User = get_user_model()


class UserLessonQuerySet(models.QuerySet):
    def avaible_for(self, user: User):
        """Возвращает уроки, которые были куплены пользователем, то есть доступные ему"""

        user_subscription = (
            UserSubscribtion.objects.filter(
                user=user, active_before__gte=timezone.now()
            )
            .select_related("subscribtion")
            .first()
        )

        if not user_subscription:
            return self.none()

        lessons_subquery = user_subscription.subscribtion.lessons.filter(
            opens_at__lte=user_subscription.active_before
        ).values("id")
        return self.filter(lesson__id__in=models.Subquery(lessons_subquery))


class UserLessonManager(models.Manager):
    def get_queryset(self):
        return (
            UserLessonQuerySet(self.model, using=self._db)
            .select_related("lesson")
            .annotate(
                title=models.F("lesson__title"), content=models.F("lesson__content")
            )
        )

    def avaible_for(self, user: User):
        return self.get_queryset().avaible_for(user)
