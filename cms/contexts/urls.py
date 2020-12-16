from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import re_path, path, include

from cms.menus.api_views import ApiMenu
from . views import *

urlpatterns = []

CMS_PATH_PREFIX = getattr(settings, 'CMS_PATH_PREFIX', '')

# uniCMS dispatcher
urlpatterns += re_path(f'{CMS_PATH_PREFIX}.*', cms_dispatch, name='cms_dispatch'),
