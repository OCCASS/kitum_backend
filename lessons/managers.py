from django.contrib.auth import get_user_model
from django.db import models

from subscribtions.models import UserSubscribtion

User = get_user_model()


class UserLessonQuerySet(models.QuerySet):
    def avaible_for(self, user: User):
        try:
            user_subscribtion = UserSubscribtion.objects.get(user=user, is_active=True)
        except UserSubscribtion.DoesNotExist:
            return self.none()
        lessons = user_subscribtion.subscribtion.lessons.values_list("id", flat=True)
        return self.filter(lesson__id__in=lessons)


class UserLessonManager(models.Manager):
    def get_queryset(self):
        return UserLessonQuerySet(self.model, using=self._db)

    def avaible_for(self, user: User):
        return self.get_queryset().avaible_for(user)
