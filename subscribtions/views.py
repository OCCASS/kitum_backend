from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from subscribtions.models import UserSubscribtion
from subscribtions.serializers import UserSubscribtionSerializer


class MySubscribtions(ListAPIView):
    queryset = UserSubscribtion.objects.all()
    serializer_class = UserSubscribtionSerializer
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user, is_active=True)
