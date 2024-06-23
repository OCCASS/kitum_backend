from django.conf import settings
from django.db import models
from django.utils import timezone


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
