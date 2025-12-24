from django.contrib import admin
from django.urls import path, include, re_path # <--- Agrega re_path
from django.conf import settings
from django.views.static import serve # <--- OJO: Agrega 'include' aquí

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),    # <--- Agrega esta línea
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]