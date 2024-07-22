from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class UserVariantManager(models.Manager):
    pass

    # def create_from(self, variant: Variant, user: User):
    #     """Create UserVariant from Variant"""
    #
    #     user_variant = UserVariant(title=variant.title, user=user)
    #     user_variant.save()
    #     tasks = []
    #     for task in variant.tasks.all():
    #         tasks.append(UserVariantTask(task=task))
    #     UserVariantTask.objects.bulk_create(tasks)
    #     user_variant.tasks.add(*tasks)
    #     user_variant.save()
    #     return user_variant
