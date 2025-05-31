from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

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


class UserCreationForm(forms.ModelForm):
    """Форма для создания пользователей в админке"""

    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Подтверждение пароля", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("email", "telegram", "first_name", "last_name")

    def clean_password2(self):
        if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
            raise forms.ValidationError("Пароли не совпадают")
        return self.cleaned_data["password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # хэшируем пароль
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Форма для редактирования пользователей в админке"""

    password = ReadOnlyPasswordHashField(label="Пароль")

    class Meta:
        model = User
        fields = (
            "email",
            "telegram",
            "password",
            "first_name",
            "last_name",
            "birthday",
            "avatar",
            "is_confirmed",
            "is_staff",
            "is_superuser",
        )

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        "email",
        "telegram",
        "first_name",
        "last_name",
        "is_staff",
        "is_confirmed",
    )
    list_filter = ("is_staff", "is_superuser", "is_confirmed")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личная информация",
            {"fields": ("first_name", "last_name", "birthday", "avatar")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_confirmed",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "telegram",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name", "telegram")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")


admin.site.register(User, UserAdmin)
