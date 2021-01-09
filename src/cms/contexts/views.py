import logging
import re

from django.conf import settings
from django.http import (Http404,
                         HttpResponseRedirect)
from django.shortcuts import render, get_object_or_404
from django.utils.module_loading import import_string

from cms.pages.models import Page
from urllib.parse import urlparse

from . decorators import unicms_cache
from . models import WebSite, WebPath
from . utils import append_slash

logger = logging.getLogger(__name__)

CMS_PATH_PREFIX = getattr(settings, 'CMS_PATH_PREFIX', '')
CMS_APP_REGEXP_URLPATHS_LOADED = {import_string(k):v
                                  for k,v in getattr(settings, 'CMS_APP_REGEXP_URLPATHS', {}).items()}


@unicms_cache
def cms_dispatch(request):
    requested_site = re.match(r'^[a-zA-Z0-9\.\-\_]*',
                              request.get_host()).group()

    website = get_object_or_404(WebSite, domain = requested_site)
    path = urlparse(request.get_full_path()).path.replace(CMS_PATH_PREFIX, '')

    _msg_head = 'APP REGEXP URL HANDLERS:'
    # detect if webpath is referred to a specialized app
    for cls,v in CMS_APP_REGEXP_URLPATHS_LOADED.items():
        logger.debug(f'{_msg_head} - {cls}: {v}')
        match = re.match(v, path)
        if not match:
            logger.debug(f'{_msg_head} - {cls}: {v} -> UNMATCH with {path}')
            continue

        query = match.groupdict()
        params = {'request': request,
                  'website': website,
                  'path': path,
                  'match': match}
        params.update(query)
        handler = cls(**params)
        try:
            return handler.as_view()
        except Exception as e: # pragma: no cover
            logger.exception(f'{path}:{e}')
            raise Http404("CMS Page not found")

    # go further with webpath matching
    path = append_slash(path)
    webpath = WebPath.objects.filter(site=website,
                                     fullpath=path).first()
    if not webpath:
        raise Http404()
    if webpath.is_alias:
        return HttpResponseRedirect(webpath.redirect_url)

    page = Page.objects.filter(webpath = webpath, is_active = True)
    published_page = page.filter(state = 'published').first()

    if request.session.get('draft_view_mode'):
        page = page.filter(state = 'draft').last() or published_page
    else:
        page = published_page

    if not page:
        raise Http404("CMS Page not found")
    context = {
        'website': website,
        'path': path,
        'webpath': webpath,
        'page': page,
    }
    return render(request, page.base_template.template_file, context)
