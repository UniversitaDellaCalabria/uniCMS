import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from urllib.parse import urlsplit

from . import settings as app_settings


CMS_URL_ALLOWED_SCHEMES = getattr(settings, 'CMS_URL_ALLOWED_SCHEMES',
                                  app_settings.CMS_URL_ALLOWED_SCHEMES)


def validate_safe_url(value):
    """
    allows relative urls and absolute urls with allowed schemes only
    (prevents javascript:, data:, vbscript: ... in links)
    """
    if not value: return
    # browsers ignore whitespaces and control chars in schemes
    # (eg: 'java\tscript:')
    normalized = re.sub(r'[\x00-\x20\x7f]', '', value).lower()
    try:
        scheme = urlsplit(normalized).scheme
    except ValueError:
        raise ValidationError(_('Invalid url'))
    if scheme and scheme not in CMS_URL_ALLOWED_SCHEMES:
        raise ValidationError(_('Url scheme not allowed: %(scheme)s'),
                              params={'scheme': scheme})
