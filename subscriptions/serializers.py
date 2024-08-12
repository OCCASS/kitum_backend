from rest_framework.serializers import CharField, ModelSerializer, Serializer, SerializerMethodField

from subscriptions.models import Subscription, UserSubscription


class UserSubscriptionSerializer(ModelSerializer):
    title = SerializerMethodField()
    price = SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = (
            "id",
            "created_at",
            "updated_at",
            "title",
            "price",
            "expires_at",
            "canceled_at",
            "status"
        )

    def get_title(self, instance: UserSubscription):
        return instance.subscription.title

    def get_price(self, instance: UserSubscription):
        return instance.subscription.price


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("id", "title", "price", "advantages")


class OrderSubscriptionSerializer(Serializer):
    return_url = CharField(required=True)
    description = CharField(required=True)
