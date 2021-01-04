import logging

from django import template
from django.conf import settings

import cms.templates.settings as app_settings

from cms.contexts.decorators import detect_language
from cms.templates.utils import import_string_block


logger = logging.getLogger(__name__)
register = template.Library()

CMS_TEMPLATE_BLOCK_SECTIONS = getattr(settings, "CMS_TEMPLATE_BLOCK_SECTIONS",
                                      app_settings.CMS_TEMPLATE_BLOCK_SECTIONS)


@register.simple_tag
def supported_languages(): # pragma: no cover
    return settings.LANGUAGES


@register.simple_tag(takes_context=True)
def blocks_in_position(context, section):
    request = context['request']
    page = context['page']
    webpath = context['webpath']

    positions_dict = dict(CMS_TEMPLATE_BLOCK_SECTIONS)
    page_blocks = page.get_blocks()
    
    for block in page_blocks:        
        if isinstance(positions_dict.get(block.section), tuple):
            sub_positions = positions_dict.get(section)
            if not sub_positions: # pragma: no cover
                logger.warning(f'Block {block} in a not existent sub '
                               f'section: {block.section}')
                return False
            
            for item in sub_positions:
                return import_string_block(block=block,
                                           request=request,
                                           page=page,
                                           webpath=webpath)
        else:
            return import_string_block(block=block,
                                       request=request,
                                       page=page,
                                       webpath=webpath)
