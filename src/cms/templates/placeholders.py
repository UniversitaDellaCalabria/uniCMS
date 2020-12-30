import logging
import random
import string

from django.utils.safestring import SafeString

from cms.carousels.models import Carousel
from cms.contexts.utils import handle_faulty_templates
from cms.menus.models import NavigationBar, NavigationBarItem
from cms.pages.models import PageLink


logger = logging.getLogger(__name__)


def _get_placeholder_by_typestring(page, placeholder_type_str):
    blocks = page.get_blocks()

    ph = [i for i in blocks if i.type == placeholder_type_str]
    return ph

def load_carousel_placeholder(context, template):
    _func_name = 'load_carousel_placeholder'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    webpath = context['webpath']
    block = context.get('block')
    page = context['page']

    carousels = page.get_carousels()
    if not carousels: return SafeString('')

    if not block:
        logger.warning(f'{_func_name} cannot get a block object')
        return SafeString('')

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
        return SafeString('')

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

def load_link_placeholder(context, template):
    _func_name = 'load_link_placeholder'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    webpath = context['webpath']
    block = context.get('block')
    page = context['page']

    links = page.get_links()
    if not links: return SafeString('')

    if not block:
        logger.warning(f'{_func_name} cannot get a block object')
        return SafeString('')

    blocks = page.get_blocks()
    ph = [i for i in blocks
          if i.type == \
          'cms.templates.blocks.LinkPlaceholderBlock']

    if not ph:
        _msg = '{} doesn\'t have any page link'.format(_log_msg)
        logger.warning(_msg)
        return SafeString('')

    for i in zip(ph, links):
        link = i[1]
        if block.__class__.__name__ == i[0].type.split('.')[-1]:
            # already rendered
            if getattr(link, '_published', False):
                continue
            data = {'link': link.url,}
            link._published = True

        return handle_faulty_templates(template, data, name=_func_name)

def load_publication_content_placeholder(context, template):
    _func_name = 'load_publication_content_placeholder'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    webpath = context['webpath']
    block = context.get('block')
    page = context['page']

    pubs = page.get_publications()
    if not pubs: return SafeString('')

    # i18n
    language = getattr(request, 'LANGUAGE_CODE', '')

    if not block:
        logger.warning(f'{_func_name} cannot get a block object')
        return SafeString('')

    ph = _get_placeholder_by_typestring(page,
            'cms.templates.blocks.PublicationContentPlaceholderBlock')

    if not ph:
        _msg = '{} doesn\'t have any page publications'.format(_log_msg)
        logger.warning(_msg)
        return SafeString('')

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

def load_media_placeholder(context, template):
    _func_name = 'load_media_placeholder'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    webpath = context['webpath']
    block = context.get('block')
    page = context['page']

    medias = page.get_medias()
    if not medias: return SafeString('')

    if not block:
        logger.warning(f'{_func_name} cannot get a block object')
        return SafeString('')

    # i18n
    language = getattr(request, 'LANGUAGE_CODE', '')

    blocks = page.get_blocks()
    ph = [i for i in blocks
          if i.type == \
          'cms.templates.blocks.MediaPlaceholderBlock']
    if not ph:
        _msg = '{} doesn\'t have any page media'.format(_log_msg)
        logger.warning(_msg)
        return SafeString('')

    for i in zip(ph, medias):
        media = i[1]
        if block.__class__.__name__ == i[0].type.split('.')[-1]:
            # already rendered
            if getattr(media, '_published', False):
                continue
            data = {'media': media.media, 'url': media.url}
            media._published = True

        return handle_faulty_templates(template, data, name=_func_name)

def load_menu_placeholder(context, template):
    _func_name = 'load_menu_placeholder'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    webpath = context['webpath']
    block = context.get('block')
    page = context['page']

    menus = page.get_menus()
    if not menus: return SafeString('')

    if not block:
        logger.warning(f'{_func_name} cannot get a block object')
        return SafeString('')

    # i18n
    language = getattr(request, 'LANGUAGE_CODE', '')

    blocks = page.get_blocks()
    ph = [i for i in blocks
          if i.type == \
          'cms.templates.blocks.MenuPlaceholderBlock']
    if not ph:
        _msg = '{} doesn\'t have any page menu'.format(_log_msg)
        logger.warning(_msg)
        return SafeString('')

    for i in zip(ph, menus):
        menu = i[1]
        if block.__class__.__name__ == i[0].type.split('.')[-1]:
            # already rendered
            if getattr(menu, '_published', False):
                continue
            items = menu.menu.get_items(lang=language,
                                        parent__isnull=True)
            data = {'items': items}
            menu._published = True

        return handle_faulty_templates(template, data, name=_func_name)
