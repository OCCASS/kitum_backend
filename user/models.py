from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from .managers import CustomUserManager
from authentication.tasks import generate_profile_image_for_user_task
from core.models import BaseModel
from subscriptions.models import UserSubscription


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
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

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            generate_profile_image_for_user_task(self)

    def get_subscriptions(self):
        return self.subscriptions.filter(status=UserSubscription.ACTIVE)


class UserSession(BaseModel):
    class Meta:
        db_table = "user_session"
        verbose_name = "Сессия пользователя"
        verbose_name_plural = "Сессии пользователей"

    user = models.ForeignKey(
        User, verbose_name="Пользователь", on_delete=models.CASCADE
    )
    jti = models.CharField("JTI", max_length=32, unique=True)
    user_agent = models.TextField("User-Agent", blank=True, null=True)
    fingerprint = models.CharField("Отпечаток", max_length=32)
    ip_address = models.GenericIPAddressField("IP-адресс", blank=True, null=True)
    is_active = models.BooleanField("Активен", default=True)

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=["is_active"])
