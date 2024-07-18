from rest_framework.serializers import CharField, ModelSerializer, Serializer

from subscriptions.models import Subscription, UserSubscription


class UserSubscriptionSerializer(ModelSerializer):
    title = CharField()
    price = CharField()

    class Meta:
        model = UserSubscription
        fields = (
            "id",
            "created_at",
            "updated_at",
            "title",
            "price",
            "active_before",
        )


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("id", "title", "price")


class OrderSubscriptionSerializer(Serializer):
    return_url = CharField(required=True)
    description = CharField(required=True)
