from core.models import BaseModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Subscription(BaseModel):
    """Модель подписки"""

    class Meta:
        db_table = "subscription"
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)


class SubscriptionOrder(BaseModel):
    """Модель заказа подписки"""

    class Meta:
        db_table = "subscription_order"
        verbose_name = "Заказ подписки"
        verbose_name_plural = "Заказы подписок"

    payment_id = models.CharField(max_length=50)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class UserSubscription(BaseModel):
    """Модель подписки пользователя"""

    class Meta:
        db_table = "user_subscription"
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    purchased_at = models.DateTimeField(default=None, null=True)
    active_before = models.DateTimeField(default=None, null=True)
