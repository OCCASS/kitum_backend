from core.models import BaseModel
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Schedule(BaseModel):
    """Модель расписания пользователя"""

    class Meta:
        db_table = "schedule"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    week_day_1 = models.IntegerField(default=settings.DEFAULT_WEEK_DAY_1)
    week_day_2 = models.IntegerField(default=settings.DEFAULT_WEEK_DAY_2)
