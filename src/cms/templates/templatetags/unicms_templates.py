import logging

from django import template
from django.conf import settings

import cms.templates.settings as app_settings

from cms.contexts.decorators import detect_language


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

    sections_dict = dict(CMS_TEMPLATE_BLOCK_SECTIONS)
    if isinstance(sections_dict.get(section), tuple):
        sub_sections = sections_dict.get(section)
        if not sub_sections: # pragma: no cover
            logger.warning(f'Block {block} in a not existent sub '
                           f'section: {block.section}')
            return False
        for sub_section in sub_sections:
            page_blocks = page.get_blocks(section=sub_section[0])
            if page_blocks: return True
        return False
    return True if page.get_blocks(section=section) else False
