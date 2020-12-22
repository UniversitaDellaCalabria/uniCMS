import logging

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import SafeString

from cms.contexts.decorators import detect_language
from cms.contexts.utils import handle_faulty_templates
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
def load_publication_content_placeholder(context, template,
                                         section = None,
                                         publication_id = None):
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

    # id is quite arbitrary
    if publication_id:
        pub = Publication.objects.filter(pk = publication_id).first()

        if not pub:
            _msg = '{} cannot find publication id {}'.format(_log_msg,
                                                             publication_id)
            logger.error(_msg)
            return ''

        pub.translate_as(lang=language)
        data = {'publication': pub}
        return handle_faulty_templates(template, data, name=_func_name)

    else:
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
                
                data = {'publication': pub}
                pub._published = True
                return handle_faulty_templates(template, data, name=_func_name)


@register.simple_tag(takes_context=True)
def load_link_placeholder(context, template,
                          aspect_ratio,
                          url='',
                          section = None):
    _func_name = 'load_link_placeholder'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    webpath = context['webpath']
    block = context.get('block')
    page = context['page']
    if not block:
        logger.warning(f'{_func_name} cannot get a block object')
        return ''

    # url is quite arbitrary
    if url:
        data = {'aspect_ratio': aspect_ratio,
                'link': url,}
        return handle_faulty_templates(template, data, name=_func_name)
    else:
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
                data = {'aspect_ratio': aspect_ratio,
                        'link': link.url,}
                link._published = True
                
            return handle_faulty_templates(template, data, name=_func_name)
