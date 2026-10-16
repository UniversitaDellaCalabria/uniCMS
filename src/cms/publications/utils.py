import logging
import nh3

from django.conf import settings
from django.utils import timezone

from .settings import (
    CMS_PUBLICATION_ALLOWED_TAGS,
    CMS_PUBLICATION_ALLOWED_ATTRIBUTES,
    CMS_PUBLICATION_ALLOWED_STYLE_PROPERTIES,
    CMS_PUBLICATION_ALLOWED_URL_SCHEMES
)


logger = logging.getLogger(__name__)

CMS_PUBLICATION_ALLOWED_TAGS = getattr(settings, 'CMS_PUBLICATION_ALLOWED_TAGS',
                                       CMS_PUBLICATION_ALLOWED_TAGS)
CMS_PUBLICATION_ALLOWED_ATTRIBUTES = getattr(settings, 'CMS_PUBLICATION_ALLOWED_ATTRIBUTES',
                                             CMS_PUBLICATION_ALLOWED_ATTRIBUTES)
CMS_PUBLICATION_ALLOWED_STYLE_PROPERTIES = getattr(settings, 'CMS_PUBLICATION_ALLOWED_STYLE_PROPERTIES',
                                                   CMS_PUBLICATION_ALLOWED_STYLE_PROPERTIES)
CMS_PUBLICATION_ALLOWED_URL_SCHEMES = getattr(settings, 'CMS_PUBLICATION_ALLOWED_URL_SCHEMES',
                                              CMS_PUBLICATION_ALLOWED_URL_SCHEMES)


def sanitize_html(value):
    """
    removes from html content all tags, attributes, styles
    and url schemes not explicitly allowed (script, iframe, on* ...)
    """
    if not value: return value
    return nh3.clean(value,
                     tags=set(CMS_PUBLICATION_ALLOWED_TAGS),
                     attributes={k: set(v) for k,v in CMS_PUBLICATION_ALLOWED_ATTRIBUTES.items()},
                     filter_style_properties=set(CMS_PUBLICATION_ALLOWED_STYLE_PROPERTIES),
                     url_schemes=set(CMS_PUBLICATION_ALLOWED_URL_SCHEMES),
                     link_rel='noopener noreferrer')


def publication_base_filter():
    # now = timezone.localtime()
    query_params = {'is_active': True,
                    # 'date_start__lte': now,
                    # 'date_end__gt': now
                    }
    return query_params


def publication_context_base_filter():
    now = timezone.localtime()
    pub_filter = publication_base_filter()
    pubcontx_filter = {'date_start__lte': now,
                       'date_end__gt': now}
    for k,v in pub_filter.items():
        pubcontx_filter[f'publication__{k}'] = v
    # pubcontx_filter = {f'publication__{k}':v
        # for k,v in pub_filter.items(),
        # }
    pubcontx_filter['is_active'] = True
    return pubcontx_filter
