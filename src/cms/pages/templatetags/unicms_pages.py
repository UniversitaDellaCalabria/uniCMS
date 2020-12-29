import logging
import string
import random

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import SafeString

from cms.carousels.models import Carousel
from cms.contexts.decorators import detect_language
from cms.contexts.utils import handle_faulty_templates
from cms.menus.models import NavigationBar, NavigationBarItem
from cms.pages.models import Category, PageBlock, PageLink, PagePublication
from cms.publications.models import Publication, PublicationContext
from cms.templates.utils import import_string_block


logger = logging.getLogger(__name__)
register = template.Library()


def _get_placeholder_by_typestring(page, placeholder_type_str):
    blocks = page.get_blocks()

    ph = [i for i in blocks if i.type == placeholder_type_str]
    return ph


@register.simple_tag(takes_context=True)
def load_blocks(context, section=None):
    request = context['request']
    page = context['page']
    webpath = context['webpath']
    blocks = page.get_blocks(section=section)

    result = SafeString('')
    if request.user.is_staff and request.session.get('show_template_blocks_sections'):
        result += render_to_string('load_blocks_head.html', {'section': section})

    for block in blocks:
        obj = import_string_block(block=block,
                                  request=request,
                                  page=page,
                                  webpath=webpath)
        try:
            result += obj.render()
        except Exception as e:
            logger.exception(('Block {} failed rendering '
                              '({}): {}').format(block, obj, e))
    return result


@register.simple_tag
def cms_categories():
    return Category.objects.values_list('name', flat=1)


@register.simple_tag(takes_context=True)
def load_page_title(context, page):
    request = context['request']
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
def load_publication_content_placeholder(context, template):
    _func_name = 'load_publication_content_placeholder'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    webpath = context['webpath']
    block = context.get('block')
    page = context['page']

    # i18n
    language = getattr(request, 'LANGUAGE_CODE', '')

    if not block:
        logger.warning(f'{_func_name} cannot get a block object')
        return ''

    pubs = page.get_publications()

    ph = _get_placeholder_by_typestring(page,
            'cms.templates.blocks.PublicationContentPlaceholderBlock')

    if not ph:
        _msg = '{} doesn\'t have any page publications'.format(_log_msg)
        logger.warning(_msg)
        return ''

    ph_pubs = [i for i in zip(ph, pubs)]
    for i in ph_pubs:
        pub = i[1].publication
        if block.__class__.__name__ == i[0].type.split('.')[-1]:
            # already rendered
            if getattr(pub, '_published', False):
                continue

            # i18n
            pub.translate_as(lang=language)

            data = {'publication': pub,
                    'webpath': webpath}
            pub._published = True
            return handle_faulty_templates(template, data, name=_func_name)


@register.simple_tag(takes_context=True)
def load_link_placeholder(context, template):
    _func_name = 'load_link_placeholder'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    webpath = context['webpath']
    block = context.get('block')
    page = context['page']
    if not block:
        logger.warning(f'{_func_name} cannot get a block object')
        return ''

    blocks = page.get_blocks()
    ph = [i for i in blocks
          if i.type == \
          'cms.templates.blocks.LinkPlaceholderBlock']

    if not ph:
        _msg = '{} doesn\'t have any page link'.format(_log_msg)
        logger.warning(_msg)
        return ''

    links = page.get_links()
    for i in zip(ph, links):
        link = i[1]
        if block.__class__.__name__ == i[0].type.split('.')[-1]:
            # already rendered
            if getattr(link, '_published', False):
                continue
            data = {'link': link.url,}
            link._published = True

        return handle_faulty_templates(template, data, name=_func_name)


@register.simple_tag(takes_context=True)
def load_carousel_placeholder(context, template):
    _func_name = 'load_carousel_placeholder'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    webpath = context['webpath']
    block = context.get('block')
    page = context['page']
    if not block:
        logger.warning(f'{_func_name} cannot get a block object')
        return ''

    # i18n
    language = getattr(request, 'LANGUAGE_CODE', '')

    # random identifier
    N = 4
    # using random.choices()
    # generating random strings
    identifier = ''.join(random.choices(string.ascii_lowercase +
                                        string.digits, k = N))

    blocks = page.get_blocks()
    ph = [i for i in blocks
          if i.type == \
          'cms.templates.blocks.CarouselPlaceholderBlock']

    if not ph:
        _msg = '{} doesn\'t have any page carousel'.format(_log_msg)
        logger.warning(_msg)
        return ''

    carousels = page.get_carousels()
    for i in zip(ph, carousels):
        page_carousel = i[1]
        if block.__class__.__name__ == i[0].type.split('.')[-1]:
            # already rendered
            if getattr(page_carousel, '_published', False):
                continue
            data = {'carousel_items': page_carousel.carousel.get_items(language),
                    'carousel_identifier': identifier}
            page_carousel._published = True

        return handle_faulty_templates(template, data, name=_func_name)


@register.simple_tag(takes_context=True)
def load_menu_placeholder(context, template):
    _func_name = 'load_menu_placeholder'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    webpath = context['webpath']
    block = context.get('block')
    page = context['page']
    if not block:
        logger.warning(f'{_func_name} cannot get a block object')
        return ''

    # i18n
    language = getattr(request, 'LANGUAGE_CODE', '')

    blocks = page.get_blocks()
    ph = [i for i in blocks
          if i.type == \
          'cms.templates.blocks.MenuPlaceholderBlock']
    if not ph:
        _msg = '{} doesn\'t have any page menu'.format(_log_msg)
        logger.warning(_msg)
        return ''

    menus = page.get_menus()
    for i in zip(ph, menus):
        page_menu = i[1]
        if block.__class__.__name__ == i[0].type.split('.')[-1]:
            # already rendered
            if getattr(page_menu, '_published', False):
                continue
            items = page_menu.menu.get_items(lang=language,
                                             parent__isnull=True)
            data = {'items': items}
            page_menu._published = True

        return handle_faulty_templates(template, data, name=_func_name)
