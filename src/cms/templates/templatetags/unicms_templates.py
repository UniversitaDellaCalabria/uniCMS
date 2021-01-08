import logging

from django import template
from django.conf import settings

import cms.templates.settings as app_settings


logger = logging.getLogger(__name__)
register = template.Library()

CMS_TEMPLATE_BLOCK_SECTIONS = getattr(settings, "CMS_TEMPLATE_BLOCK_SECTIONS",
                                      app_settings.CMS_TEMPLATE_BLOCK_SECTIONS)


@register.simple_tag
def supported_languages(): # pragma: no cover
    return settings.LANGUAGES


@register.simple_tag(takes_context=True)
def blocks_in_position(context, section):
    context['request']
    page = context['page']
    context['webpath']

    sections_dict = dict(CMS_TEMPLATE_BLOCK_SECTIONS)
    if isinstance(sections_dict.get(section), tuple):
        sub_sections = sections_dict.get(section)
        if not sub_sections: # pragma: no cover
            logger.warning(f"Section {section} hasn't sub-sections")
            return False
        for sub_section in sub_sections:
            page_blocks = page.get_blocks(section=sub_section[0])
            if page_blocks: return True
        logger.warning(f'No blocks in {section} sub-sections')
        return False
    return True if page.get_blocks(section=section) else False
