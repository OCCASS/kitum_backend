from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from subscriptions.exceptions import AlreadyCanceled


class Subscription(BaseModel):
    """Модель подписки"""

    class Meta:
        db_table = "subscription"
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    advantages = ArrayField(models.CharField(max_length=120), blank=False)
    with_home_work = models.BooleanField()

    def __str__(self):
        return str(self.title)


class SubscriptionOrder(BaseModel):
    """Модель заказа подписки"""

    class Meta:
        db_table = "subscription_order"
        verbose_name = "Заказ подписки"
        verbose_name_plural = "Заказы подписок"

    payment_id = models.CharField(max_length=50)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey("user.User", on_delete=models.SET_NULL, null=True)


class UserSubscription(BaseModel):
    """Модель подписки пользователя"""

    ACTIVE = "active"
    CANCELED = "canceled"
    STATUS_CHOICES = {ACTIVE: "Активная", CANCELED: "Отменена"}

    class Meta:
        db_table = "user_subscription"
        verbose_name = "Подписка пользователя"
        verbose_name_plural = "Подписки пользователей"

    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    purchased_at = models.DateTimeField(default=None, null=True)
    canceled_at = models.DateTimeField(default=None, null=True, blank=True)
    expires_at = models.DateField(default=None, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="subscription"
    )

    def cancel(self):
        if self.canceled_at:
            raise AlreadyCanceled

        self.status = self.CANCELED
        self.canceled_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.user.email} ({self.subscription.title})"
