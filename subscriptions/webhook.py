import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from ipware import get_client_ip
from lessons.models import Lesson, UserLesson, UserLessonTask
from yookassa.domain.common import SecurityHelper
from yookassa.domain.notification import (
    WebhookNotificationEventType,
    WebhookNotificationFactory,
)

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
            subscription_order = SubscriptionOrder.objects.get(
                payment_id=notification.object.id
            )
            user, subscription = (
                subscription_order.user,
                subscription_order.subscription,
            )
            if is_user_have_active_subscription(subscription, user):
                return HttpResponse(status=200)

            renew_or_create_user_subscription(subscription, user)
            create_user_lessons(subscription, user)

            return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=400)


def is_user_have_active_subscription(subscription, user: User) -> bool:
    return UserSubscription.objects.filter(
        user=user, active_before__gte=timezone.now(), subscription=subscription
    ).exists()


def renew_or_create_user_subscription(subscription: Subscription, user: User):
    """Создает или продлевает подписку пользователя в зависимости от того куплена она у него или нет"""

    try:
        active_user_subscription = UserSubscription.objects.get(
            subscription=subscription, user=user, active_before__lte=timezone.now()
        )
        renew_user_subscription(active_user_subscription)
    except ObjectDoesNotExist:
        new_user_subscription(subscription, user)


def new_user_subscription(subscription: Subscription, user: User) -> None:
    """Создает подписку для пользователя"""

    now = timezone.now()
    active_before = now.replace(month=(now.month + 1) % 12)
    UserSubscription(
        subscription=subscription,
        user=user,
        purchased_at=now,
        active_before=active_before,
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
