from django.apps import AppConfig


class LessonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lessons"

    def ready(self):
        import lessons.signals
