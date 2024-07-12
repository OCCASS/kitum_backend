from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import BaseModel

User = get_user_model()


class UserScheduleConfig(BaseModel):
    """Модель конфигурации расписания для пользователя"""

    class Meta:
        db_table = "user_schedule_config"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    week_day_1 = models.IntegerField(default=settings.DEFAULT_WEEK_DAY_1)
    week_day_2 = models.IntegerField(default=settings.DEFAULT_WEEK_DAY_2)


class Holiday(models.Model):
    """Модель, когда будут праздники, дни отдыха и все такое"""

    class Meta:
        db_table = "holiday"

    id = models.AutoField(primary_key=True)
    day = models.PositiveIntegerField(
        validators=(MinValueValidator(1), MaxValueValidator(31))
    )
    month = models.PositiveIntegerField(
        validators=(MinValueValidator(1), MaxValueValidator(12))
    )
