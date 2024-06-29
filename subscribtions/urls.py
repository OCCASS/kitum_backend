from django.urls import path

from subscribtions.views import MySubscribtions

urlpatterns = [path("my/", MySubscribtions.as_view(), name="my_subscribtions")]
