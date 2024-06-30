from django.contrib.auth import get_user_model
from django.db import models

from core.models import BaseModel

User = get_user_model()


class Subscription(BaseModel):
    """Модель подписки"""

    class Meta:
        db_table = "subscription"

    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)


class UserSubscription(BaseModel):
    """Модель подписки пользователя"""

    class Meta:
        db_table = "user_subscription"

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    purchased_at = models.DateTimeField(default=None, null=True)
    active_before = models.DateTimeField(default=None, null=True)
