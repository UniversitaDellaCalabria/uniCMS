from cms.contexts.settings import CMS_CACHE_KEY_PREFIX


LOCKS_CACHE_ENABLED = True
LOCKS_CACHE_KEY_PREFIX = f'{CMS_CACHE_KEY_PREFIX}locks_'
# in seconds
LOCKS_CACHE_TTL = 20
