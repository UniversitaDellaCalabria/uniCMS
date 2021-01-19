import logging

from django.utils import timezone


logger = logging.getLogger(__name__)


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
