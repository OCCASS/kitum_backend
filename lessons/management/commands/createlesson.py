import datetime
from argparse import ArgumentParser

from django.core.management.base import BaseCommand, CommandError

from lessons.models import Lesson
from services import streaming
from subscriptions.models import Subscription
from tasks.models import Task


class Command(BaseCommand):
    help = "Create lesson"

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--title", type=str, required=True)
        parser.add_argument("--description", type=str, default="")
        parser.add_argument(
            "--opens_at",
            type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d"),
            required=True,
        )
        parser.add_argument("--task_ids", nargs="+", type=str, default=[])
        parser.add_argument("--subscription_ids", nargs="+", type=str, default=[])

    def handle(self, *args, **options):
        title: str = options.get("title", "")
        try:
            video_id = streaming.create_event(title)
        except streaming.CreatingEventError as e:
            self.stdout.write(self.style.ERROR(e))
            return

        lesson = Lesson.objects.create(
            title=title,
            description=options.get("description"),
            opens_at=options.get("opens_at"),
            kinescope_video_id=video_id,
        )

        tasks = Task.objects.filter(id__in=options.get("task_ids"))
        lesson.tasks.add(*tasks)

        subscriptions = Subscription.objects.filter(
            id__in=options.get("subscription_ids")
        )
        lesson.subscriptions.add(*subscriptions)

        self.stdout.write(
            self.style.SUCCESS("Lesson successfully created, id is: %s" % lesson.id)
        )
