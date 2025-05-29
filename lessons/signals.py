from django.db.models.base import post_save
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils import timezone

from lessons.models import Lesson
from lessons.models import UserLesson
from lessons.services import create_kinescope_live_event
from lessons.services import CreateKinescopeEventError
from subscriptions.models import UserSubscription
from tasks.models import Task
from tasks.models import UserTask


@receiver(post_save, sender=Lesson)
def on_lesson_create(sender, instance: Lesson, created, **kwargs):
    if created and instance.kinescope_video_id is None:
        try:
            event_id = create_kinescope_live_event(
                instance.title, protected=True, auto_start=True
            )
            instance.kinescope_video_id = event_id
            instance.save()
        except CreateKinescopeEventError as e:
            raise e


@receiver(m2m_changed, sender=Lesson.tasks.through)
def create_user_tasks_on_task_added(sender, instance: Lesson, action, pk_set, **kwargs):
    if action == "post_add":
        new_task_ids = pk_set

        user_lessons = UserLesson.objects.filter(lesson=instance)

        for user_lesson in user_lessons:
            for task_id in new_task_ids:
                task = Task.objects.get(pk=task_id)
                if not user_lesson.tasks.filter(task=task).exists():
                    user_task = UserTask.objects.create(
                        task=task, user=user_lesson.user
                    )
                    user_lesson.tasks.add(user_task)


@receiver(m2m_changed, sender=Lesson.subscriptions.through)
def create_user_tasks_on_subscriptions_added(
    sender, instance: Lesson, action, pk_set, **kwargs
):
    if action == "post_add":
        user_subscriptions = UserSubscription.objects.filter(
            subscription__in=instance.subscriptions.all(),
            status=UserSubscription.ACTIVE,
        ).select_related("user", "subscription")

        for user_sub in user_subscriptions:
            UserLesson.objects.get_or_create(
                lesson=instance,
                user=user_sub.user,
                defaults={
                    "complete_tasks_deadline": timezone.now(),
                    "subscription": user_sub.subscription,
                },
            )
