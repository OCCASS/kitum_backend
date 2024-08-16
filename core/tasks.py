from celery import shared_task
from django.contrib.auth.models import send_mail
from django.conf import settings


@shared_task
def send_mail_task(subject: str, message: str, recipient_list: list[str]):
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
