import logging
import urllib

from django import template
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from cms.contexts.models import WebPath, WebSite
from cms.contexts.utils import handle_faulty_templates, sanitize_path

logger = logging.getLogger(__name__)
register = template.Library()


def _build_breadcrumbs(webpath: str):
    nodes = webpath.split('/')
    if nodes[-1] == '':
        del nodes[-1]

    crumbs = []
    root = '/'
    root_prefixed = f'/{settings.CMS_PATH_PREFIX}'

    for i in nodes:
        url = sanitize_path(f'{root}/{i}')
        node_webpath = WebPath.objects.filter(fullpath=f'{url}/').first()
        node_name = node_webpath.name if node_webpath else i
        node_path = sanitize_path(f'{root_prefixed}{url}/')
        crumbs.append((node_path, node_name))
        root = url
    crumbs[0] = [root_prefixed, _('Home')]
    return crumbs


@register.simple_tag(takes_context=True)
def language_menu(context, template=None):
    request = context['request']
    languages = {k:v for k,v in dict(settings.LANGUAGES).items()}
    current_args = urllib.parse.urlencode(request.GET)
    data = {v:f'?{current_args}&lang={k}' for k,v in languages.items()}
    if template: # pragma: no cover
        return handle_faulty_templates(template, data, name='language_menu')
    return data


@register.simple_tag
def breadcrumbs(webpath, template=None, leaf=None):
    template = template or 'breadcrumbs.html'
    crumbs = _build_breadcrumbs(webpath.fullpath)
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
