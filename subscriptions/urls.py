from django.urls import path

from subscriptions.views import OrderSubscription, SubscriptionsList, CancelSubscription

from .webhook import payment_webhook

urlpatterns = [
    path("", SubscriptionsList.as_view(), name="subscription_list"),
    path("payment/webhook/", payment_webhook, name="payment_webhook"),
    path("<uuid:pk>/order/", OrderSubscription.as_view(), name="payment_webhook"),
    path("cancel/", CancelSubscription.as_view(), name="cancel_subscription"),
]
