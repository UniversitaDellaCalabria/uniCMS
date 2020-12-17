import logging
import os

from django.conf import settings
from django.utils import timezone

from . import settings as app_settings

logger = logging.getLogger(__name__)


def load_app_settings():
    for i in dir(app_settings):
        if i[0] == '_': continue
        globals()[i] = getattr(settings, i, 
                               getattr(app_settings, i))


def publication_base_filter():
    now = timezone.localtime()
    query_params = {'is_active': True,
                    'date_start__lte': now,
                    'date_end__gt': now
                    }
    return query_params


def publication_context_base_filter():
    pub_filter = publication_base_filter()
    pubcontx_filter = {f'publication__{k}':v 
                       for k,v in pub_filter.items()}
    pubcontx_filter['is_active'] = True
    return pubcontx_filter
