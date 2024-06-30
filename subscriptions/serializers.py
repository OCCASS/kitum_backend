from rest_framework.serializers import CharField, ModelSerializer

from subscriptions.models import UserSubscription


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
