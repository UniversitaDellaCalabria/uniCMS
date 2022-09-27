from django.conf import settings
from django.urls import path, re_path

from . settings import CMS_MEDIA_HANDLER_PATH
from . views import *


CMS_MEDIA_HANDLER_PATH = getattr(settings, 'CMS_MEDIA_HANDLER_PATH', CMS_MEDIA_HANDLER_PATH)
urlpatterns = []

urlpatterns += path(f'{CMS_MEDIA_HANDLER_PATH}/<str:unique_code>/', get_media_file, name='media-file'),
