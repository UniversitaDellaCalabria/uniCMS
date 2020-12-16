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
def supported_languages():
    return settings.LANGUAGES


@register.simple_tag(takes_context=True)
def blocks_in_position(context, position=None):
    request = context['request']
    page = context['page']
    webpath = context['webpath']

    positions_dict = dict(CMS_TEMPLATE_BLOCK_SECTIONS)

    if isinstance(positions_dict.get(position), tuple):
        sub_positions = positions_dict[position]
        for item in sub_positions:
            page_blocks = page.get_blocks(section=item[0])
            for block in page_blocks:
                obj = import_string_block(block=block,
                                          request=request,
                                          page=page,
                                          webpath=webpath)
                if obj: return True
    else:
        page_blocks = page.get_blocks(section=position)
        for block in page_blocks:
            obj = import_string_block(block=block,
                                      request=request,
                                      page=page,
                                      webpath=webpath)
            if obj: return True
    return False
