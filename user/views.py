from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.serializers import UserSerializer
from .serializers import EditUserAvatarSerializer, EditUserSerializer

User = get_user_model()


class UserView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_object(self) -> User:
        user = self.request.user
        self.check_object_permissions(self.request, user)
        return user


class EditUserView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = EditUserSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(user, context=self.get_serializer_context()).data)

    def get_object(self) -> User:
        user = self.request.user
        self.check_object_permissions(self.request, user)
        return user

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class EditUserAvatarView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = EditUserAvatarSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_obj = request.FILES["avatar"]
        user = self.get_object()
        self.update_user_avatar(user, file_obj)

        return Response(
            UserSerializer(user, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def get_object(self) -> User:
        user = self.request.user
        self.check_object_permissions(self.request, user)
        return user

    def update_user_avatar(self, user: User, avatar):
        user.avatar = avatar
        user.save()
