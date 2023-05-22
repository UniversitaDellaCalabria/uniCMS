import logging

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import SafeString

from cms.contexts.utils import handle_faulty_templates
from cms.publications.models import Category
from cms.templates.utils import import_string_block


logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag(takes_context=True)
def load_blocks(context, section=None):
    result = SafeString('')

    if not section: return result

    request = context.get('request', None)
    page = context.get('page', None)
    webpath = context.get('webpath', None)

    blocks = context.get('page_blocks', page.get_blocks())
    # menus = context.get('menus', None)

    if not blocks: return result

    if not all((request, page, webpath)): return result

    #blocks = page.get_blocks()

    logger.debug(f'load_blocks section: {section}')

    if request.user.is_staff and request.session.get('show_template_blocks_sections'):
        result += render_to_string('load_blocks_head.html', {'section': section})

    for block in blocks:
        if block.section == section:
            obj = import_string_block(block=block,
                                      request=request,
                                      page=page,
                                      webpath=webpath,
                                      blocks=blocks,)
                                      # menus=menus)
            try:
                result += obj.render() or SafeString('')
            except Exception as e: # pragma: no cover
                logger.exception(('Block {} failed rendering '
                                  '({}): {}').format(block, obj, e))
    return result


@register.simple_tag
def cms_categories():
    return Category.objects.values_list('name', flat=1)


@register.simple_tag(takes_context=True)
def load_page_title(context):
    request = context['request']
    page = context['page']
    language = getattr(request, 'LANGUAGE_CODE', '')
    page.translate_as(lang=language)
    return page.title


@register.simple_tag(takes_context=True)
def load_link(context, template, url):
    _func_name = 'load_link'

    # url is quite arbitrary
    data = {'link': url}
    return handle_faulty_templates(template, data, name=_func_name)


@register.simple_tag(takes_context=True)
def load_page_publications(context, template):
    _func_name = 'load_publications'
    request = context['request']
    page = context['page']
    language = getattr(request, 'LANGUAGE_CODE', '')
    page_publications = page.get_publications()
    for page_pub in page_publications:
        page_pub.publication.translate_as(lang=language)
    data = {'page_publications': page_publications}
    return handle_faulty_templates(template, data, name=_func_name)
