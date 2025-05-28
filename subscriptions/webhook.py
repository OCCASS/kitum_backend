import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from ipware import get_client_ip
from yookassa.domain.common import SecurityHelper
from yookassa.domain.notification import WebhookNotificationEventType
from yookassa.domain.notification import WebhookNotificationFactory

from .models import Subscription
from .models import SubscriptionOrder
from .models import UserSubscription
from lessons.models import UserLesson
from tasks.models import UserTask

User = get_user_model()

logger = logging.getLogger(__name__)


"""
@csrf_exempt
def payment_webhook(request, *args, **kwargs):
    # TODO: add prev month subscription order
    ip, _ = get_client_ip(request)
    if not SecurityHelper().is_ip_trusted(ip):
        logger.error(f"Webhook call from not trusted ip - {ip}")
        return HttpResponse(status=400)

    data = json.loads(request.body)
    try:
        notification = WebhookNotificationFactory().create(data)
        if notification.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
            subscription_order = SubscriptionOrder.objects.get(
                payment_id=notification.object.id
            )
            user, subscription = (
                subscription_order.user,
                subscription_order.subscription,
            )
            user_subscription: UserSubscription = user.get_subscriptions()
            if user_subscription:
                lessons_from = user_subscription.expires_at
                renew_user_subscription(user_subscription)
            else:
                lessons_from = timezone.localdate()
                user_subscription = new_user_subscription(subscription, user)
            lessons_to = user_subscription.expires_at
            create_user_lessons(subscription, user, (lessons_from, lessons_to))
            return HttpResponse(status=200)
    except Exception as e:
        logger.error(f"{e.__class__.__name__}{e.args}")
        return HttpResponse(status=400)
"""


def _get_expires_at_from_today() -> timezone.localdate:
    today = timezone.localdate()
    next_month = (today.month + 1) % 12
    return today.replace(month=next_month)


def new_user_subscription(subscription: Subscription, user: User) -> UserSubscription:
    """Создает подписку для пользователя"""

    user_subscription = UserSubscription(
        subscription=subscription,
        purchased_at=timezone.now(),
        expires_at=_get_expires_at_from_today(),
        user=user,
    )
    user_subscription.save()
    return user_subscription


def renew_user_subscription(user_subscription: UserSubscription) -> None:
    """Продлевает подписку пользователя еще на 1 месяц"""

    if user_subscription.status == UserSubscription.CANCELED:
        expires_at = _get_expires_at_from_today()
    else:
        next_month = (user_subscription.expires_at.month + 1) % 12
        expires_at = user_subscription.expires_at.replace(month=next_month)

    user_subscription.expires_at = expires_at
    user_subscription.purchased_at = timezone.now()
    user_subscription.status = UserSubscription.ACTIVE
    user_subscription.save()


def create_user_lessons(
    subscription: Subscription, user: User, period: tuple[timezone, timezone]
) -> None:
    """Создать уроки пользователя на купленный месяц, в следствии покупки подписки"""

    from_, to = period
    exists_lessons = UserLesson.objects.filter(user=user).values_list(
        "lesson_id", flat=True
    )
    lessons = (
        subscription.lesson_set.filter(opens_at__gte=from_, opens_at__lte=to)
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
