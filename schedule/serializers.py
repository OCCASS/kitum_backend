from rest_framework import serializers

from .models import *


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ("day", "month")
