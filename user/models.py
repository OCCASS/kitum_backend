from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from core.models import BaseModel
from subscriptions.models import UserSubscription
from .managers import CustomUserManager


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    """Модель пользователя"""

    class Meta:
        db_table = "user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    first_name = models.CharField(max_length=120, null=False)
    last_name = models.CharField(max_length=120, null=False)
    avatar = models.FileField(upload_to="avatar")
    email = models.EmailField(null=False, unique=True)
    password = models.CharField(max_length=256)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True)
    is_confirmed = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "last_name")

    objects = CustomUserManager()
