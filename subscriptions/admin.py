from django.contrib import admin

from .models import Subscription
from .models import UserSubscription

admin.site.register(Subscription)
admin.site.register(UserSubscription)
