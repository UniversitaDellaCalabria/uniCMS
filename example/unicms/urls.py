"""unicms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework import routers, permissions
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.schemas import get_schema_view

try:
    from rest_framework.schemas.agid_schema_views import get_schema_view
except:
    from rest_framework.schemas import get_schema_view


ADMIN_PATH = getattr(settings, 'ADMIN_PATH', 'admin')

urlpatterns = [
    path(f'{ADMIN_PATH}/', admin.site.urls),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API
router = routers.DefaultRouter()
urlpatterns += re_path('^api', include(router.urls)),

# API schemas
try:
    urlpatterns += re_path('^openapi$',
                            get_schema_view(**settings.OAS3_CONFIG),
                            name='openapi-schema'),
    urlpatterns += re_path('^openapi.json$',
                           get_schema_view(renderer_classes = [JSONOpenAPIRenderer],
                                        **settings.OAS3_CONFIG),
                           name='openapi-schema-json'),
except:
    urlpatterns += re_path('^openapi$',
                            get_schema_view(**{}),
                            name='openapi-schema'),
    urlpatterns += re_path('^openapi.json$',
                           get_schema_view(renderer_classes = [JSONOpenAPIRenderer],
                                        **{}),
                           name='openapi-schema-json'),

if 'cms.contexts' in settings.INSTALLED_APPS:
    urlpatterns += path('',
                        include(('cms.contexts.urls', 'cms'), namespace="unicms"),
                        name="unicms"),

if 'cms.api' in settings.INSTALLED_APPS:
    urlpatterns += path('',
                        include(('cms.api.urls', 'cms'), namespace="unicms_api"),
                        name="unicms_api"),


if 'cms.search' in settings.INSTALLED_APPS:
    urlpatterns += path('',
                        include(('cms.search.urls', 'cms_search'), namespace="unicms_search"),
                        name="unicms_search"),


if 'unicms_editorial_board' in settings.INSTALLED_APPS:
    urlpatterns += path('',
                        include(('unicms_editorial_board.urls', 'unicms_editorial_board'),
                                 namespace="unicms_editorial_board"),
                        name="unicms_editorial_board"),

