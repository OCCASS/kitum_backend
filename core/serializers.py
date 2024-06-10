from django.contrib.auth import get_user_model, password_validation
from rest_framework.serializers import ModelSerializer

User = get_user_model()


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "created_at", "password")
        extra_kwargs = {"id": {"read_only": True}, "password": {"write_only": True}}

    def save(self, **kwargs):
        return self.Meta.model.objects.create_user(**self.validated_data)

    @staticmethod
    def validate_password(data: str) -> str:
        password_validation.validate_password(password=data, user=User)
        return data
