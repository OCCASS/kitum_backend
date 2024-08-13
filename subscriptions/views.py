from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import Response

from services.payment import create_payment
from subscriptions.exceptions import UserAlreadyHaveSubscription
from subscriptions.models import Subscription, SubscriptionOrder, UserSubscription
from subscriptions.serializers import (
    OrderSubscriptionSerializer,
    SubscriptionSerializer,
    UserSubscriptionSerializer
)


class SubscriptionsList(ListAPIView):
    queryset = Subscription.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SubscriptionSerializer


class CancelSubscription(GenericAPIView):
    queryset = UserSubscription.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSubscriptionSerializer

    def post(self, request, *args, **kwargs):
        # TODO: or create cancellation request, because if user cancel subscription and after that buy new cancellation will be forgoten
        user_subscription = request.user.get_subscription()
        subscription = get_object_or_404(UserSubscription, pk=user_subscription.id, user=request.user)
        subscription.cancel()
        return Response({})


class OrderSubscription(GenericAPIView):
    serializer_class = OrderSubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if self.request.user.get_subscription():
            raise UserAlreadyHaveSubscription

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
