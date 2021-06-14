import logging
import urllib

from django import template
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from cms.contexts.models import WebPath, WebSite
from cms.contexts.utils import handle_faulty_templates

logger = logging.getLogger(__name__)
register = template.Library()


def _build_breadcrumbs(webpath: WebPath):
    crumbs = []
    root_prefixed = f'/{settings.CMS_PATH_PREFIX}'
    if webpath.parent:
        crumbs = _build_breadcrumbs(webpath.parent)
        crumbs.append((webpath.get_full_path, webpath.name))
    else:
        crumbs.append((root_prefixed, _('Home')))
    return crumbs


@register.simple_tag(takes_context=True)
def language_menu(context, template=None):
    request = context['request']
    languages = {k:v for k,v in dict(settings.LANGUAGES).items()}
    get_params = dict(request.GET)
    get_params.pop('lang', False)
    current_args = urllib.parse.urlencode(get_params)
    char = '&' if current_args else ''
    data = {v:f'?{current_args}{ char }lang={k}' for k,v in languages.items()}
    if template: # pragma: no cover
        return handle_faulty_templates(template, data, name='language_menu')
    return data


@register.simple_tag
def breadcrumbs(webpath, template=None, leaf=None):
    template = template or 'breadcrumbs.html'
    # crumbs = _build_breadcrumbs(webpath.fullpath)
    crumbs = _build_breadcrumbs(webpath)
    if leaf: # pragma: no cover
        for i in leaf.breadcrumbs:
            crumbs.append(i)
    data = {'breadcrumbs': crumbs}
    return handle_faulty_templates(template, data, name='breadcrumbs')


@register.simple_tag
def call(obj, method, **kwargs):
    return getattr(obj, method)(**kwargs)


@register.simple_tag
def cms_sites():
    return WebSite.objects.filter(is_active=True).values_list('name', 'domain')
