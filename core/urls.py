from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin_url = f"{settings.DJANGO_ADMIN_URL.strip('/')}/"

urlpatterns = [
    path(admin_url, admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("api.urls")),
    path("", include("guard.urls")),
    path("", include("shared.urls")),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
