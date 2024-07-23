import json

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from ipware import get_client_ip
from yookassa.domain.common import SecurityHelper
from yookassa.domain.notification import (
    WebhookNotificationEventType,
    WebhookNotificationFactory,
)

from lessons.models import Lesson, UserLesson, UserLessonTask
from .models import Subscription, SubscriptionOrder, UserSubscription

User = get_user_model()


@csrf_exempt
def payment_webhook(request, *args, **kwargs):
    """Webhook оплаты подписки"""

    # TODO: add prev month subscription order
    ip, _ = get_client_ip(request)
    if not SecurityHelper().is_ip_trusted(ip):
        return HttpResponse(status=400)

    data = json.loads(request.body)
    try:
        notification = WebhookNotificationFactory().create(data)
        if notification.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
            subscription_order = SubscriptionOrder.objects.get(payment_id=notification.object.id)
            user, subscription = (
                subscription_order.user,
                subscription_order.subscription,
            )
            user_subscription = user.get_subscription()
            if user_subscription:
                renew_user_subscription(user_subscription)
                return HttpResponse(status=200)

            new_user_subscription(subscription, user)
            create_user_lessons(subscription, user)

            return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=400)


def new_user_subscription(subscription: Subscription, user: User) -> None:
    """Создает подписку для пользователя"""

    now = timezone.now()
    active_before = now.replace(month=(now.month + 1) % 12)
    UserSubscription(
        subscription=subscription,
        purchased_at=now,
        active_before=active_before,
        user=user
    ).save()


def renew_user_subscription(user_subscription: UserSubscription) -> None:
    """Продлевает подписку пользователя еще на 1 месяц"""

    active_before = user_subscription.active_before.replace(
        month=(user_subscription.active_before.month + 1) % 12
    )
    user_subscription.active_before = active_before
    user_subscription.purchased_at = timezone.now()
    user_subscription.save()


def create_user_lessons(subscription: Subscription, user: User) -> None:
    """Создать уроки пользователя на купленный месяц, в следствии покупки подписки"""

    current_month = timezone.now().month
    exists_lessons = UserLesson.objects.filter(user=user).values_list(
        "lesson_id", flat=True
    )
    lessons = (
        Lesson.objects.filter(
            subscriptions__id=subscription.id, created_at__month=current_month
        )
        .exclude(id__in=exists_lessons)
        .order_by("created_at")
        .prefetch_related("subscriptions", "tasks")
    )

    user_lessons = []
    for lesson in lessons:
        user_lesson = UserLesson(
            lesson=lesson,
            user=user,
            opens_at=timezone.now(),
            complete_tasks_deadline=timezone.now(),
        )
        user_lessons.append(user_lesson)

    with transaction.atomic():
        created_user_lessons = UserLesson.objects.bulk_create(user_lessons)
        lesson_to_user_lesson = {ul.lesson_id: ul for ul in created_user_lessons}

        user_lesson_tasks = []
        for lesson in lessons:
            user_lesson = lesson_to_user_lesson[lesson.id]
            for task in lesson.tasks.all():
                user_lesson_tasks.append(UserLessonTask(lesson=user_lesson, task=task))

        UserLessonTask.objects.bulk_create(user_lesson_tasks)
