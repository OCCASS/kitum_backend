from rest_framework.serializers import CharField, ModelSerializer

from subscribtions.models import UserSubscribtion


class UserSubscribtionSerializer(ModelSerializer):
    title = CharField()
    price = CharField()

    class Meta:
        model = UserSubscribtion
        fields = (
            "id",
            "created_at",
            "updated_at",
            "title",
            "price",
            "active_before",
        )
