import hashlib
import json
import logging
import re
import urllib

from collections import OrderedDict
from django.conf import settings
from django.core.cache import cache

from . import settings as app_settings

logger = logging.getLogger(__name__)


# unicms cache
CMS_CACHE_TTL = getattr(settings, 'CMS_CACHE_TTL',
                        app_settings.CMS_CACHE_TTL)
CMS_CACHE_EXCLUDED_MATCHES = getattr(settings,
                                     'CMS_CACHE_EXCLUDED_MATCHES',
                                     app_settings.CMS_CACHE_EXCLUDED_MATCHES)
CMS_CACHE_KEY_PREFIX = getattr(settings,
                               'CMS_CACHE_KEY_PREFIX',
                               app_settings.CMS_CACHE_KEY_PREFIX)
CMS_CACHE_MAX_ENTRIES = getattr(settings,
                                'CMS_CACHE_MAX_ENTRIES',
                                app_settings.CMS_CACHE_MAX_ENTRIES)
CMS_CACHE_ENABLED = getattr(settings,
                            'CMS_CACHE_ENABLED',
                            app_settings.CMS_CACHE_ENABLED)


def make_cache_key(request):
    v = request.get_raw_uri()
    up = urllib.parse.urlparse(v)
    q = urllib.parse.parse_qs(up.query)
    qs = OrderedDict(sorted(q.items()))
    if 'lang' not in qs.keys():
        qs['lang'] = [request.LANGUAGE_CODE]
    qs_ser = json.dumps(dict(qs))

    value_key = f'{up.netloc}_{up.path}_{qs_ser}'
    hashed_v = hashlib.sha256(value_key.encode()).hexdigest()
    cache_key = f'{CMS_CACHE_KEY_PREFIX}{hashed_v}'
    return cache_key


def get_from_cache(request):
    key = make_cache_key(request)
    res = cache.get(key)
    if res:
        logger.debug(f'uniCMS Cache - {key} succesfully taken from cache')
        return res


def set_to_cache(request, value):
    if not CMS_CACHE_MAX_ENTRIES or \
       len(cache.keys(f'{CMS_CACHE_KEY_PREFIX}*')) < CMS_CACHE_MAX_ENTRIES:
        key = make_cache_key(request)
        cache.set(key, value, CMS_CACHE_TTL)
        logger.debug(f'uniCMS Cache - {key} succesfully stored to cache')
        return True


def is_request_cacheable(request):
    for excluded in CMS_CACHE_EXCLUDED_MATCHES:
        if re.findall(excluded, request.get_raw_uri(), re.I):
            return False
    return True


def is_response_cacheable(response):
    return response.status_code == 200


def is_cache_available():
    return CMS_CACHE_ENABLED
