from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import re_path, path, include

from . import api_views

urlpatterns = []

CMS_PATH_PREFIX = getattr(settings, 'CMS_PATH_PREFIX', '')

# Public API Resources
urlpatterns += path(f'api/search',
                    api_views.ApiSearchEngine.as_view(),
                    name='api-search-engine'),

