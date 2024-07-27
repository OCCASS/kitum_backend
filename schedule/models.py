from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import BaseModel

User = get_user_model()


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
