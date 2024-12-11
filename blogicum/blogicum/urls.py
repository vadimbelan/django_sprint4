from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler403, handler404, handler500
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'pages.views.page_not_found_custom'
handler500 = 'pages.views.server_error_custom'
handler403 = 'pages.views.csrf_failure'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/', include('django.contrib.auth.urls')),
    path('reg/', include('pages.reg_urls')),
]

if settings.DEBUG:
    urlpatterns += (static
                    (settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
