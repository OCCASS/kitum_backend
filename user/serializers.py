from django.contrib.auth import get_user_model, password_validation
from rest_framework.serializers import CharField, FileField, Serializer
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from subscriptions.serializers import UserSubscriptionSerializer

User = get_user_model()


class UserSerializer(ModelSerializer):
    avatar = SerializerMethodField()
    subscription = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "created_at",
            "password",
            "avatar",
            "subscription",
            "birthday",
        )
        extra_kwargs = {"id": {"read_only": True}, "password": {"write_only": True}}

    def get_avatar(self, obj: User):
        request = self.context.get("request")
        if request and obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return ""

    def get_subscription(self, obj: User):
        subscription = obj.get_subscription()
        if subscription:
            return UserSubscriptionSerializer(subscription).data
        return None

    def save(self, **kwargs):
        return self.Meta.model.objects.create_user(**self.validated_data)

    @staticmethod
    def validate_password(data: str) -> str:
        password_validation.validate_password(password=data, user=User)
        return data


class EditUserSerializer(Serializer):
    first_name = CharField(required=True, allow_blank=False)
    last_name = CharField(required=True, allow_blank=False)

    def update(self, instance: User, validated_data):
        instance.first_name = validated_data["first_name"]
        instance.last_name = validated_data["last_name"]
        instance.save()
        return instance


class EditUserAvatarSerializer(Serializer):
    avatar = FileField(required=True)
