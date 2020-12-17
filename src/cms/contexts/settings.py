from django.utils.translation import gettext_lazy as _


CMS_CONTEXT_PERMISSIONS = (('1', _('can edit created by him/her in his/her context')),
                           ('2', _('can edit all pages in his/her context')),
                           ('3', _('can edit all pages in his/her context and descendants')),
                           ('4', _('can translate all pages in his/her context')),
                           ('5', _('can translate all pages in his/her context and descendants')),
                           ('6', _('can publish created by him/her in his/her context')),
                           ('7', _('can publish all pages in his/her context')),
                           ('8', _('can publish all pages in his/her context and descendants')),
                           )

CMS_CACHE_ENABLED = True
CMS_CACHE_KEY_PREFIX = 'unicms_'
# in seconds
CMS_CACHE_TTL = 25
# set to 0 means infinite
CMS_MAX_ENTRIES = 0
# request.get_raw_uri() that matches the following would be not cached
CMS_CACHE_EXCLUDED_MATCHES =  ['/search?',]


