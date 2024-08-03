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

from lessons.models import Lesson, UserLesson
from tasks.models import UserTask
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
            user_subscription: UserSubscription = user.get_subscription()
            if user_subscription:
                lessons_from = user_subscription.active_before
                renew_user_subscription(user_subscription)
            else:
                lessons_from = timezone.localdate()
                new_user_subscription(subscription, user)
            lessons_before = user_subscription.active_before
            create_user_lessons(subscription, user, (lessons_from, lessons_before))
            return HttpResponse(status=200)
    except Exception as e:
        # TODO: add logging
        return HttpResponse(status=400)


def new_user_subscription(subscription: Subscription, user: User) -> None:
    """Создает подписку для пользователя"""

    now = timezone.now()
    active_before = timezone.localdate().replace(month=(now.month + 1) % 12)
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


def create_user_lessons(subscription: Subscription, user: User, period: tuple[timezone, timezone]) -> None:
    """Создать уроки пользователя на купленный месяц, в следствии покупки подписки"""

    from_, before = period
    exists_lessons = UserLesson.objects.filter(user=user).values_list(
        "lesson_id", flat=True
    )
    lessons = (
        subscription.lesson_set.filter(opens_at__gte=from_, opens_at__lte=before)
        .exclude(id__in=exists_lessons)
        .order_by("created_at")
        .prefetch_related("subscriptions", "tasks")
    )

    user_lessons = []
    for lesson in lessons:
        user_lesson = UserLesson(
            lesson=lesson,
            user=user,
            complete_tasks_deadline=timezone.now(),
        )
        user_lessons.append(user_lesson)

    with transaction.atomic():
        created_user_lessons = UserLesson.objects.bulk_create(user_lessons)
        lesson_to_user_lesson = {ul.lesson_id: ul for ul in created_user_lessons}

        for lesson in lessons:
            tasks = []
            user_lesson = lesson_to_user_lesson[lesson.id]

            for task in lesson.tasks.all():
                tasks.append(UserTask(task=task))

            UserTask.objects.bulk_create(tasks)

            user_lesson.tasks.add(*tasks)
            user_lesson.save()
