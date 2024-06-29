from django.db import models
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from subscribtions.models import UserSubscribtion
from subscribtions.serializers import UserSubscribtionSerializer


class MySubscribtions(ListAPIView):
    queryset = (
        UserSubscribtion.objects.all()
        .select_related("subscribtion")
        .annotate(
            title=models.F("subscribtion__title"), price=models.F("subscribtion__price")
        )
    )
    serializer_class = UserSubscribtionSerializer
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, queryset):
        return queryset.filter(
            user=self.request.user, active_before__gte=timezone.now()
        )
