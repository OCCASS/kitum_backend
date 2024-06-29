from rest_framework.serializers import ModelSerializer, SerializerMethodField

from subscribtions.models import UserSubscribtion


class UserSubscribtionSerializer(ModelSerializer):
    title = SerializerMethodField()
    price = SerializerMethodField()

    class Meta:
        model = UserSubscribtion
        fields = ("id", "created_at", "updated_at", "title", "price")

    def get_title(self, obj: UserSubscribtion):
        return obj.subscribtion.title

    def get_price(self, obj: UserSubscribtion):
        return obj.subscribtion.price
