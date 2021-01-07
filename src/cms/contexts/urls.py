from django.conf import settings
from django.urls import re_path

from . views import cms_dispatch

urlpatterns = []

CMS_PATH_PREFIX = getattr(settings, 'CMS_PATH_PREFIX', '')

# uniCMS dispatcher
urlpatterns += re_path(f'{CMS_PATH_PREFIX}.*', cms_dispatch, name='cms_dispatch'),
