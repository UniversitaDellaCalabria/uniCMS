from django.utils.translation import gettext_lazy as _


CMS_CONTEXT_PERMISSIONS = (
                           (0, _('disable permissions in context')),

                           (1, _('can translate content in their own context')),
                           (2, _('can translate content in their own context and descendants')),

                           (3, _('can edit content created by them in their own context')),
                           (4, _('can edit content in their own context')),
                           (5, _('can edit content in their own context and descendants')),

                           (6, _('can publish content in their own context')),
                           (7, _('can publish content in their own context and descendants')),
                          )

CMS_CACHE_ENABLED = True
CMS_CACHE_KEY_PREFIX = 'unicms_'
# in seconds
CMS_CACHE_TTL = 25
# set to 0 means infinite
CMS_CACHE_MAX_ENTRIES = 0
# request.get_raw_uri() that matches the following would be not cached
CMS_CACHE_EXCLUDED_MATCHES = ['/search?',]
