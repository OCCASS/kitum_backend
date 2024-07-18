from django.db import models
from django.utils import timezone
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response
from services.payment import create_payment

from subscriptions.models import Subscription, SubscriptionOrder, UserSubscription
from subscriptions.serializers import (
    OrderSubscriptionSerializer,
    SubscriptionSerializer,
    UserSubscriptionSerializer,
)


class SubscriptionsList(ListAPIView):
    queryset = Subscription.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscriptionSerializer


class OrderSubscription(GenericAPIView):
    serializer_class = OrderSubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subscription = self.get_object()
        payment = create_payment(
            subscription.price,
            serializer.data["return_url"],
            serializer.data["description"],
        )
        self.create_order(subscription, payment.id)

        return Response({"confirmation_url": payment.confirmation.confirmation_url})

    def create_order(self, subscription, payment_id):
        SubscriptionOrder(
            subscription=subscription, user=self.request.user, payment_id=payment_id
        ).save()

    def get_object(self):
        return Subscription.objects.get(pk=self.kwargs.get("pk"))


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
