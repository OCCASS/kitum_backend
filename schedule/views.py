from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import *


class HolidaysListView(ListAPIView):
    queryset = Holiday.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = HolidaySerializer
