from django.db import models


class UserTaskManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("task")
            .annotate(
                kim_number=models.F("task__kim_number"),
                cost=models.F("task__cost"),
                content=models.F("task__content"),
                type=models.F("task__type"),
            )
        )
