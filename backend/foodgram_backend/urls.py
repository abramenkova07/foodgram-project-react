from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/', include(
            [
                path('', include('api.urls'))
            ]
        )
    ),
    path(
        'redoc/',
        TemplateView.as_view(template_name='api/redoc.html'),
        name='redoc'
    )
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
