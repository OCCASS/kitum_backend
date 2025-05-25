from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from lessons.models import Lesson
from lessons.models import UserLesson
from tasks.models import Task
from tasks.models import UserTask


@receiver(m2m_changed, sender=Lesson.tasks.through)
def create_user_tasks_on_task_added(sender, instance: Lesson, action, pk_set, **kwargs):
    if action == "post_add":
        new_task_ids = pk_set

        user_lessons = UserLesson.objects.filter(lesson=instance)

        for user_lesson in user_lessons:
            for task_id in new_task_ids:
                task = Task.objects.get(pk=task_id)
                if not user_lesson.tasks.filter(task=task).exists():
                    user_task = UserTask.objects.create(task=task)
                    user_lesson.tasks.add(user_task)
