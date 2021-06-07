import logging

from django.conf import settings
from django.core.cache import cache

from . import settings as app_settings

logger = logging.getLogger(__name__)


# locks timed cache
LOCKS_CACHE_TTL = getattr(settings, 'LOCKS_CACHE_TTL',
                          app_settings.LOCKS_CACHE_TTL)
LOCKS_CACHE_KEY_PREFIX = getattr(settings, 'LOCKS_CACHE_KEY_PREFIX',
                                 app_settings.LOCKS_CACHE_KEY_PREFIX)
LOCK_MESSAGE = getattr(settings, 'LOCK_MESSAGE', app_settings.LOCK_MESSAGE)


def get_lock_from_cache(content_type_id, object_id):
    key = f'{LOCKS_CACHE_KEY_PREFIX}{content_type_id}_{object_id}'
    res = cache.get(key)
    if res: # pragma: no cover
        logger.debug(f'uniCMS locks timed cache - {key} succesfully taken from cache')
        return (res, cache.ttl(key))
    return (0, 0)


def set_lock_to_cache(user_id, content_type_id, object_id):
    key = f'{LOCKS_CACHE_KEY_PREFIX}{content_type_id}_{object_id}'
    cache.set(key, user_id, LOCKS_CACHE_TTL)
    logger.debug(f'uniCMS locks timed cache - {key} succesfully stored to cache')
