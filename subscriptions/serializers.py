from rest_framework.serializers import CharField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer
from rest_framework.serializers import SerializerMethodField

from subscriptions.models import Subscription
from subscriptions.models import UserSubscription


class UserSubscriptionSerializer(ModelSerializer):
    title = SerializerMethodField()
    price = SerializerMethodField()
    with_home_work = SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = (
            "id",
            "created_at",
            "updated_at",
            "title",
            "price",
            "with_home_work",
            "canceled_at",
            "status",
        )

    def get_title(self, instance: UserSubscription) -> str:
        return instance.subscription.title

    def get_price(self, instance: UserSubscription) -> int:
        return instance.subscription.price

    def get_with_home_work(self, instance: UserSubscription) -> bool:
        return instance.subscription.with_home_work


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("id", "title", "price", "advantages", "with_home_work")


class OrderSubscriptionSerializer(Serializer):
    return_url = CharField(required=True)
    description = CharField(required=True)
