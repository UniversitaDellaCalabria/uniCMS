import logging

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import SafeString

from cms.contexts.decorators import detect_language
from cms.contexts.utils import handle_faulty_templates
from cms.pages.models import Category
from cms.publications.models import PublicationContext
from cms.templates.utils import import_string_block


logger = logging.getLogger(__name__)
register = template.Library()


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
