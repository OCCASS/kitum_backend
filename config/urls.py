from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("api/v1/lessons/", include("lessons.urls")),
    path("api/v1/variants/", include("variants.urls")),
    path("api/v1/user/", include("user.urls")),
    path("api/v1/subscriptions/", include("subscriptions.urls")),
    path("api/v1/schedule/", include("schedule.urls")),
    path("api/v1/payment/", include("payment.urls")),
    path("auth/", include("authentication.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
