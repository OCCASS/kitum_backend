from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class PasswordReset(models.Model):
    """Модель для хранения пары ключ - email"""

    class Meta:
        db_table = "password_reset"

    email = models.EmailField()
    token = models.CharField(max_length=100)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.expires_at = timezone.now() + settings.PASSWORD_RESET_TOKEN_LIFETIME
        return super().save(*args, **kwargs)


class ConfirmMail(models.Model):
    """Модель для хранения токена подтверждения email"""

    class Meta:
        db_table = "confirm_mail"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.expires_at = timezone.now() + settings.CONFIRM_MAIL_TOKEN_LIFETIME
        return super().save(*args, **kwargs)
