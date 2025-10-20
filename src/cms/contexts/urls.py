from django.conf import settings
from django.shortcuts import redirect
from django.urls import path, re_path

from . views import *

urlpatterns = []

CMS_PATH_PREFIX = getattr(settings, 'CMS_PATH_PREFIX', '')

# uniCMS dispatcher
if CMS_PATH_PREFIX:
    urlpatterns += path('', lambda req: redirect(f'/{CMS_PATH_PREFIX}')),

urlpatterns += path('pages/<int:page_id>/preview/', pagePreview, name='page-preview'),

urlpatterns += re_path('^(?:$|.+\/)$', cms_dispatch, name='cms_dispatch'),
