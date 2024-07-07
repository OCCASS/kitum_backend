from django.urls import path

from .views import *

urlpatterns = [
    path("", ScheduleListView.as_view(), name="schedule"),
    path("holidays/", HolidaysListView.as_view(), name="holidays"),
]
