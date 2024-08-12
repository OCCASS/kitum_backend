from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionManager
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from subscriptions.models import UserSubscription
from .managers import CustomUserManager


class User(BaseModel, AbstractBaseUser, PermissionManager):
    """Модель пользователя"""

    class Meta:
        db_table = "user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    first_name = models.CharField(max_length=120, null=False)
    last_name = models.CharField(max_length=120, null=False)
    birthday = models.DateField(null=True)
    avatar = models.FileField(upload_to="avatar")
    email = models.EmailField(null=False, unique=True)
    password = models.CharField(max_length=256)
    is_confirmed = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "last_name")

    objects = CustomUserManager()

    def get_subscription(self):
        return self.subscription.filter(status=UserSubscription.ACTIVE, expires_at__gt=timezone.now()).first()
