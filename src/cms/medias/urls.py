from django.conf import settings
from django.urls import path, re_path

from . views import *


urlpatterns = []

urlpatterns += path(f'{settings.MEDIA_URL[1:-1]}/uuid/<str:unique_code>/', get_media_file, name='media-file'),
