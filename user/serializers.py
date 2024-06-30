from django.contrib.auth import get_user_model
from rest_framework.serializers import CharField, FileField, Serializer

User = get_user_model()


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
