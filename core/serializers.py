from django.contrib.auth import get_user_model, password_validation
from rest_framework.serializers import ModelSerializer, SerializerMethodField

User = get_user_model()


class UserSerializer(ModelSerializer):
    avatar = SerializerMethodField()

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
        )
        extra_kwargs = {"id": {"read_only": True}, "password": {"write_only": True}}

    def get_avatar(self, obj: User):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.avatar.url)
        return ""

    def save(self, **kwargs):
        return self.Meta.model.objects.create_user(**self.validated_data)

    @staticmethod
    def validate_password(data: str) -> str:
        password_validation.validate_password(password=data, user=User)
        return data
