from django.conf import settings
from django.shortcuts import redirect
from django.urls import path, re_path

from cms.contexts.views import pagePreview
from . views import cms_dispatch

urlpatterns = []

CMS_PATH_PREFIX = getattr(settings, 'CMS_PATH_PREFIX', '')

# uniCMS dispatcher

if CMS_PATH_PREFIX:
    urlpatterns += path('', lambda req: redirect(f'/{CMS_PATH_PREFIX}')),

urlpatterns += re_path(f'{CMS_PATH_PREFIX}.*', cms_dispatch, name='cms_dispatch'),

urlpatterns += path('pages/<int:page_id>/preview/', pagePreview, name='page-preview'),
