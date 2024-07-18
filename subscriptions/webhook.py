import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from lessons.models import Lesson, UserLesson, UserLessonTask
from .models import SubscriptionOrder, UserSubscription, Subscription

User = get_user_model()


@csrf_exempt
def payment_webhook(request, *args, **kwargs):
    """Webhook оплаты подписки"""

    # TODO: check double lessons create
    # TODO: add prev month subscription order

    data = json.loads(request.body)
    if data["event"] == "payment.succeeded":
        subscription_order = SubscriptionOrder.objects.get(payment_id=data["object"]["id"])
        user, subscription = subscription_order.user, subscription_order.subscription
        if is_user_have_active_subscription(user):
            return HttpResponse(status=200)

        renew_or_create_user_subscription(subscription, user)
        create_user_lessons(subscription, user)

    return HttpResponse(status=200)


def is_user_have_active_subscription(user: User) -> bool:
    return UserSubscription.objects.filter(usersubscription__user=user).exists()


def renew_or_create_user_subscription(subscription: Subscription, user: User):
    """Создает или продлевает подписку пользователя в зависимости от того куплена она у него или нет"""

    try:
        active_user_subscription = UserSubscription.objects.get(
            subscription=subscription,
            user=user,
            active_before__lte=timezone.now()
        )
        renew_user_subscription(active_user_subscription)
    except ObjectDoesNotExist:
        new_user_subscription(subscription, user)


def new_user_subscription(subscription: Subscription, user: User) -> None:
    """Создает подписку для пользователя"""

    now = timezone.now()
    active_before = now.replace(month=(now.month + 1) % 12)
    UserSubscription(subscription=subscription, user=user, purchased_at=now, active_before=active_before).save()


def renew_user_subscription(user_subscription: UserSubscription) -> None:
    """Продлевает подписку пользователя еще на 1 месяц"""

    active_before = user_subscription.active_before.replace(month=(user_subscription.active_before.month + 1) % 12)
    user_subscription.active_before = active_before
    user_subscription.purchased_at = timezone.now()
    user_subscription.save()


def create_user_lessons(subscription: Subscription, user: User) -> None:
    """Создать уроки пользователя на купленный месяц, в следствии покупки подписки"""

    current_month = timezone.now().month
    lessons = Lesson.objects. \
        filter(subscriptions__id=subscription.id, created_at__month=current_month). \
        order_by("created_at"). \
        prefetch_related("subscriptions"). \
        prefetch_related("tasks")

    # TODO: add bulk create
    for lesson in lessons:
        user_lesson = UserLesson(lesson=lesson, user=user, opens_at=timezone.now())
        user_lesson.save()
        for task in lesson.tasks.all():
            UserLessonTask(lesson=user_lesson, task=task).save()
