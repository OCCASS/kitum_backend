from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsOwner

from .models import *
from .serializers import *


class LessonsView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class UserLessonsView(ListAPIView):
    queryset = UserLesson.objects.all()
    serializer_class = UserLessonSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)
