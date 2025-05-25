from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core.views import handler404 as custom_handler404
from core.views import handler500 as custom_handler500

admin.site.site_header = "KIUTM Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/lessons/", include("lessons.urls")),
    path("api/v1/variants/", include("variants.urls")),
    path("api/v1/user/", include("user.urls")),
    path("api/v1/subscriptions/", include("subscriptions.urls")),
    path("api/v1/schedule/", include("schedule.urls")),
    path("auth/", include("authentication.urls")),
]

handler404 = custom_handler404
handler500 = custom_handler500

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
