from django.utils.translation import gettext_lazy as _

from cms.contexts.settings import CMS_CACHE_KEY_PREFIX


LOCKS_CACHE_ENABLED = True
LOCKS_CACHE_KEY_PREFIX = f'{CMS_CACHE_KEY_PREFIX}locks_'
# in seconds
LOCKS_CACHE_TTL = 20
LOCK_MESSAGE = _("{user} is currently editing this "
                 "item. Unable to make changes "
                 "for at least {ttl} seconds")
FORM_SOURCE_LABEL = 'api_source'
