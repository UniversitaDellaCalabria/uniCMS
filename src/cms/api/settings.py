from django.utils.translation import gettext_lazy as _

from cms.contexts.settings import CMS_CACHE_KEY_PREFIX


LOCKS_CACHE_ENABLED = True
LOCKS_CACHE_KEY_PREFIX = f'{CMS_CACHE_KEY_PREFIX}locks_'
# in seconds
LOCKS_CACHE_TTL = 25
LOCK_MESSAGE = _("Unable to make changes. "
                 "{user} is currently editing this item")
FORM_SOURCE_LABEL = 'api_source'
