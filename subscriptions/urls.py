from django.urls import path
from subscriptions.views import MySubscriptions

urlpatterns = [path("my/", MySubscriptions.as_view(), name="my_subscriptions")]
