from django.contrib import admin

from .models import User
from .models import UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at", "is_active")
    readonly_fields = (
        "user",
        "jti",
        "user_agent",
        "fingerprint",
        "ip_address",
        "created_at",
        "updated_at",
    )


admin.site.register(User)
