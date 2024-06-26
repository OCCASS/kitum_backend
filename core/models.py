import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionManager
from django.db import models

from .managers import CustomUserManager


class BaseModel(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class User(BaseModel, AbstractBaseUser, PermissionManager):
    """Модель пользователя"""

    class Meta:
        db_table = "user"

    first_name = models.CharField(max_length=120, null=False)
    last_name = models.CharField(max_length=120, null=False)
    avatar = models.FileField(upload_to="avatar")
    email = models.EmailField(null=False, unique=True)
    password = models.CharField(max_length=256)
    is_confirmed = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "last_name")

    objects = CustomUserManager()
