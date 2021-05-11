from django.conf import settings
from django.urls import path

from . import api_views

urlpatterns = []

CMS_PATH_PREFIX = getattr(settings, 'CMS_PATH_PREFIX', '')

# Public API Resources
urlpatterns += path('api/search/',
                    api_views.ApiSearchEngine.as_view(),
                    name='api-search-engine'),
