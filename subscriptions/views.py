from django.db import models
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from subscriptions.models import UserSubscription
from subscriptions.serializers import UserSubscriptionSerializer


class MySubscriptions(ListAPIView):
    queryset = (
        UserSubscription.objects.all()
        .select_related("subscription")
        .annotate(
            title=models.F("subscription__title"), price=models.F("subscription__price")
        )
    )
    serializer_class = UserSubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, queryset):
        return queryset.filter(
            user=self.request.user, active_before__gte=timezone.now()
        )
