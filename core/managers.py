from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self, first_name: str, last_name: str, email: str, password: str, **extra_fields
    ):
        email = self.normalize_email(email)
        user = self.model(
            first_name=first_name.capitalize(),
            last_name=last_name.capitalize(),
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self, first_name: str, last_name: str, email: str, password: str, **extra_fields
    ):
        user = self.create_user(first_name, last_name, email, password, **extra_fields)
        user.is_staff = True
        user.save()
        return user
