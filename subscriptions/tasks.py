from celery import shared_task

from .models import UserSubscription


@shared_task
def notify_subscription_overdue():
    pass
