import datetime

from django.utils import timezone
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lessons.models import UserLesson

from .serializers import *


class ScheduleListView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        lesson_events = self.create_lesson_events()
        homework_events = self.create_homework_events()
        events = lesson_events + homework_events
        return Response(events)

    def create_lesson_events(self):
        lessons = self.get_lessons()
        return LessonEventSerializer(lessons, many=True).data

    def create_homework_events(self):
        lessons = self.get_lessons()
        return HomeworkEventSerializer(lessons, many=True).data

    def get_lessons(self):
        from_date, to_date = self.get_from_date(), self.get_to_date()
        queryset = UserLesson.objects.filter(user=self.request.user)
        if from_date:
            queryset = queryset.filter(lesson__opens_at__gte=from_date)
        if to_date:
            queryset = queryset.filter(lesson__opens_at__lte=to_date)
        return queryset

    def get_from_date(self) -> datetime.date:
        from_timestamp = self.request.query_params.get("from")
        try:
            from_date = datetime.datetime.fromtimestamp(int(from_timestamp)).date()
            return from_date
        except (ValueError, TypeError):
            return None

    def get_to_date(self) -> datetime.date:
        to_timestamp = self.request.query_params.get("to")
        try:
            to_date = datetime.datetime.fromtimestamp(int(to_timestamp)).date()
            return to_date
        except (ValueError, TypeError):
            return None


class HolidaysListView(ListAPIView):
    queryset = Holiday.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = HolidaySerializer
