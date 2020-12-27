from django.utils.translation import gettext_lazy as _


CMS_CONTEXT_PERMISSIONS = (('1', _('edit created by them in their own context')),
                           ('2', _('edit all pages in their own context')),
                           ('3', _('edit all pages in their own context and descendants')),
                           ('4', _('translate all pages in their own context')),
                           ('5', _('translate all pages in their own context and descendants')),
                           ('6', _('publish created by them in their own context')),
                           ('7', _('publish all pages in their own context')),
                           ('8', _('publish all pages in their own context and descendants')),
                           )

CMS_CACHE_ENABLED = True
CMS_CACHE_KEY_PREFIX = 'unicms_'
# in seconds
CMS_CACHE_TTL = 25
# set to 0 means infinite
CMS_MAX_ENTRIES = 0
# request.get_raw_uri() that matches the following would be not cached
CMS_CACHE_EXCLUDED_MATCHES =  ['/search?',]


