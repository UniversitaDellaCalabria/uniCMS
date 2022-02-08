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
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path

from rest_framework import permissions #, routers
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.schemas import get_schema_view

from . views import unicms_sitemap

try:
    from rest_framework.schemas.agid_schema_views import get_schema_view
except:
    from rest_framework.schemas import get_schema_view


ADMIN_PATH = getattr(settings, 'ADMIN_PATH', 'admin')
CMS_PATH_PREFIX = getattr(settings, 'CMS_PATH_PREFIX', '')

urlpatterns = [
    path(f'{ADMIN_PATH}/', admin.site.urls),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API
# router = routers.DefaultRouter()
# urlpatterns += re_path('^api/', include(router.urls)),

# API schemas
try:
    urlpatterns += re_path('^openapi$',
                            get_schema_view(public=True, **settings.OAS3_CONFIG),
                            name='openapi-schema'),
    urlpatterns += re_path('^openapi.json$',
                           get_schema_view(renderer_classes = [JSONOpenAPIRenderer],
                                           public=True, **settings.OAS3_CONFIG),
                           name='openapi-schema-json'),
except:
    urlpatterns += re_path('^openapi$',
                            get_schema_view(public=True, **{}),
                            name='openapi-schema'),
    urlpatterns += re_path('^openapi.json$',
                           get_schema_view(renderer_classes = [JSONOpenAPIRenderer],
                                           public=True, **{}),
                           name='openapi-schema-json'),

# sitemap
urlpatterns += re_path(r'^' + CMS_PATH_PREFIX + 'sitemap.xml$', unicms_sitemap, name='unicms_sitemap'),

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
                        include(('unicms_editorial_board.urls',
                                 'unicms_editorial_board'),
                                 namespace="unicms_editorial_board"),
                        name="unicms_editorial_board"),


if 'unicms_calendar' in settings.INSTALLED_APPS:
    urlpatterns += path('',
                        include(('unicms_calendar.urls',
                                 'unicms_calendar'),
                                 namespace="unicms_calendar"),
                        name="unicms_calendar"),


if 'saml2_sp' in settings.INSTALLED_APPS:
    from djangosaml2 import saml2_views

    import saml2_sp.urls

    urlpatterns += path('', include((saml2_sp.urls, 'sp',))),

    urlpatterns += path('{}/login/'.format(settings.SAML2_URL_PREFIX),
                           saml2_views.LoginView.as_view(), name='login'),
    urlpatterns += path('{}/acs/'.format(settings.SAML2_URL_PREFIX),
                           saml2_views.AssertionConsumerServiceView.as_view(), name='saml2_acs'),
    urlpatterns += path('{}/logout/'.format(settings.SAML2_URL_PREFIX),
                           saml2_views.LogoutInitView.as_view(), name='logout'),
    urlpatterns += path('{}/ls/'.format(settings.SAML2_URL_PREFIX),
                           saml2_views.LogoutView.as_view(), name='saml2_ls'),
    urlpatterns += path('{}/ls/post/'.format(settings.SAML2_URL_PREFIX),
                           saml2_views.LogoutView.as_view(), name='saml2_ls_post'),
    urlpatterns += path('{}/metadata/'.format(settings.SAML2_URL_PREFIX),
                           saml2_views.MetadataView.as_view(), name='saml2_metadata'),
else:
    urlpatterns += path('{}/login/'.format(settings.LOCAL_URL_PREFIX),
                        auth_views.LoginView.as_view(template_name='login.html'),
                        name='login'),
    urlpatterns += path('{}/logout/'.format(settings.LOCAL_URL_PREFIX),
                        auth_views.LogoutView.as_view(template_name='logout.html', next_page='/'),
                        name='logout'),
