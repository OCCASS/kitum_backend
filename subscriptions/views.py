from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response

from services.payment import create_payment
from subscriptions.exceptions import UserAlreadyHaveSubscription
from subscriptions.models import Subscription
from subscriptions.models import SubscriptionOrder
from subscriptions.models import UserSubscription
from subscriptions.serializers import OrderSubscriptionSerializer
from subscriptions.serializers import SubscriptionSerializer


class SubscriptionsList(ListAPIView):
    queryset = Subscription.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SubscriptionSerializer


class OrderSubscription(GenericAPIView):
    serializer_class = OrderSubscriptionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subscription = self.get_object()

        # TODO: maybe add expires_at check or set anywhere to status without expirse_at
        exists = UserSubscription.objects.filter(
            user=self.request.user,
            status=UserSubscription.ACTIVE,
            subscription=subscription,
        ).exists()

        if exists:
            raise UserAlreadyHaveSubscription

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
