from django.contrib.auth import get_user_model
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.serializers import UserSerializer

from .serializers import EditUserSerializer

User = get_user_model()


class UserView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_object(self):
        return self.request.user


class EditUserView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = EditUserSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.first_name = serializer.validated_data["first_name"].capitalize()
        user.last_name = serializer.validated_data["last_name"].capitalize()
        user.save()
        return Response(UserSerializer(user, context={"request": request}).data)
