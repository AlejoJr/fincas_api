from django.contrib import admin
from django.views.static import serve
from django.conf import settings
from django.urls import path, include, re_path
from rest_framework.documentation import include_docs_urls


urlpatterns = [
    path('fincasapi/admin/', admin.site.urls, name='admin'),
    path('fincasapi/docs/', include_docs_urls(title='Fincas API')),
    path('fincasapi/api-auth/', include('rest_framework.urls'), name='rest_framework'),
    re_path(r'fincasapi/download/(?P<path>.*)$', serve, {'document_root': settings.MI_DIRECTORIO}),

    path('fincasapi/v1/', include('fincas_api.router'), name='base_api'),
]
