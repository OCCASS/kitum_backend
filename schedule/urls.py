from django.urls import path

from .views import *

urlpatterns = [path("holidays/", HolidaysListView.as_view(), name="holidays")]
