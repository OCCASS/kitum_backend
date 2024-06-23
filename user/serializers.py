from rest_framework.serializers import CharField, Serializer


class EditUserSerializer(Serializer):
    first_name = CharField(required=True, allow_blank=False)
    last_name = CharField(required=True, allow_blank=False)
