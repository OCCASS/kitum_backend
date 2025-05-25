from django.db import models


class UserTaskManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("task")
            .annotate(
                content=models.F("task__content"),
                type=models.F("task__type"),
            )
        )
