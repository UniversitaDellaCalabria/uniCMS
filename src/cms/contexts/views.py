import logging
import re

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.http import (Http404,
                         HttpResponse,
                         HttpResponseForbidden,
                         HttpResponseRedirect)
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from cms.pages.models import Page
from cms.publications.models import PublicationContext

from urllib.parse import urlparse

from . import settings as app_settings
from . decorators import unicms_cache
from . models import EditorialBoardEditors, WebSite, WebPath
from . utils import append_slash, is_editor


logger = logging.getLogger(__name__)

CMS_PATH_PREFIX = getattr(settings, 'CMS_PATH_PREFIX', '')
CMS_APP_REGEXP_URLPATHS_LOADED = {import_string(k):v
                                  for k,v in getattr(settings, 'CMS_APP_REGEXP_URLPATHS', {}).items()}
SITEMAP_NEWS_PRIORITY = getattr(settings, 'SITEMAP_NEWS_PRIORITY',
                                app_settings.SITEMAP_NEWS_PRIORITY)
SITEMAP_WEBPATHS_PRIORITY = getattr(settings, 'SITEMAP_WEBPATHS_PRIORITY',
                                    app_settings.SITEMAP_WEBPATHS_PRIORITY)
ROBOTS_SETTINGS = getattr(settings, 'ROBOTS_SETTINGS', app_settings.ROBOTS_SETTINGS)

def _get_site_from_host(request):
    requested_site = re.match(r'^[a-zA-Z0-9\.\-\_]*',
                              request.get_host()).group()

    website = get_object_or_404(WebSite,
                                domain=requested_site,
                                is_active=True)
    return website


@unicms_cache
def cms_dispatch(request):

    website = _get_site_from_host(request)

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
            raise Http404(_("CMS Page not found"))

    # go further with webpath matching
    path = append_slash(path)
    webpath = get_object_or_404(WebPath,
                                site=website,
                                fullpath=path,
                                is_active=True)
    if webpath.is_alias:
        return HttpResponseRedirect(webpath.redirect_url)

    page = Page.objects.filter(webpath = webpath, is_active = True)
    published_page = page.filter(state = 'published').first()

    if request.session.get('draft_view_mode'):
        page = page.filter(state='draft').last() or published_page
    else:
        page = published_page

    if not page:
        raise Http404(_("CMS Page not found"))

    context = {
        'website': website,
        'path': path,
        'webpath': webpath,
        'page': page,
        'page_blocks': page.get_blocks(),
        # 'menus': page.get_menus()
    }

    # access level
    access_level = webpath.get_access_level()
    if access_level == '0':
        return render(request, page.base_template.template_file, context)
    elif not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next=//{website.domain}{webpath.get_full_path()}")
    elif request.user.is_superuser:
        return render(request, page.base_template.template_file, context)
    elif getattr(request.user, access_level, None):
        return render(request, page.base_template.template_file, context)
    return HttpResponseForbidden(_("User unauthorized"))


@staff_member_required
def pagePreview(request, page_id):
    page = get_object_or_404(Page.objects.select_related('webpath'),
                             pk=page_id)
    webpath = page.webpath
    website = webpath.site
    if not website.is_managed_by(request.user):
        return HttpResponse(_("Permission Denied on this website"))
    permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                      user=request.user)
    editor_perms = is_editor(permission)
    if not editor_perms:
        return HttpResponse(_("Permission Denied on this webpath"))

    context = {
        'website': website,
        # 'path': webpath.get_full_path(),
        'preview_mode': True,
        'webpath': webpath,
        'page': page,
        'page_blocks': page.get_blocks(),
    }
    return render(request, page.base_template.template_file, context)


def base_unicms_sitemap(request):
    website = _get_site_from_host(request)
    protocol =  request.scheme

    webpaths_map = {
        'queryset': WebPath.objects.filter(site=website,
                                           is_active=True,
                                           alias__isnull=True,
                                           alias_url=""),
        'date_field': 'modified',
    }
    # news_map = {
        # 'queryset': PublicationContext.objects.filter(webpath__site=website,
                                                      # webpath__is_active=True,
                                                      # date_start__lte=timezone.localtime(),
                                                      # date_end__gte=timezone.localtime(),
                                                      # publication__is_active=True),
        # 'date_field': 'modified',
    # }

    sitemap_dict = {
        'webpaths': GenericSitemap(webpaths_map,
                                   priority=SITEMAP_WEBPATHS_PRIORITY,
                                   protocol=protocol),
        # 'news': GenericSitemap(news_map,
                               # priority=SITEMAP_NEWS_PRIORITY,
                               # protocol=protocol)
        }

    sitemaps = sitemap(request, sitemaps=sitemap_dict)
    return HttpResponse(sitemaps.render(), content_type='text/xml')


def unicms_robots(request):
    website = _get_site_from_host(request)
    protocol =  request.scheme
    sitemap_url = reverse('unicms_sitemap')
    content = ''
    settings = ROBOTS_SETTINGS.get(website.domain, ROBOTS_SETTINGS['*'])
    for setting in settings:
        for user_agent in setting['User-agent']:
            content += f'User-agent: {user_agent}\n'
        for allow in setting['Allow']:
            content += f'Allow: {allow}\n'
        for disallow in setting['Disallow']:
            content += f'Disallow: {disallow}\n'

        content += '\n'

    content += f'Sitemap: {request.scheme}://{website.domain}{sitemap_url}'
    return HttpResponse(content, content_type='text/plain')
