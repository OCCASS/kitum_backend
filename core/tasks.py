from celery import shared_task
from django.contrib.auth.models import send_mail


@shared_task
def send_mail_task(subject: str, message: str, from_email: str, recipient_list: list[str]):
    send_mail(subject, message, from_email, recipient_list)
