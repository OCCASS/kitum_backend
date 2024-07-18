from django.urls import path

from subscriptions.views import MySubscriptions, OrderSubscription, UnpurchasedSubscriptionsList

from .webhook import payment_webhook

urlpatterns = [
    path("unpurchased/", UnpurchasedSubscriptionsList.as_view(), name="unpurchased_subscription_list"),
    path("my/", MySubscriptions.as_view(), name="my_subscriptions"),
    path("payment/webhook/", payment_webhook, name="payment_webhook"),
    path("<str:pk>/order/", OrderSubscription.as_view(), name="payment_webhook"),
]
