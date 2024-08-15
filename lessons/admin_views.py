from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from subscriptions.models import Subscription
from .models import Lesson
from .serializers import LessonSerializer, CreateLessonSerializer


class AllLessonsView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)


class CreateLessonView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = CreateLessonSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)
