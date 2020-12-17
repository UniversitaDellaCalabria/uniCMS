import logging

from django import template

from cms.pages.models import PageCarousel
from cms.contexts.utils import handle_faulty_templates


logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag(takes_context=True)
def load_carousel(context, section, template):
    request = context['request']
    
    page = PageCarousel.objects.filter(section=section,
                                       is_active=True,
                                       page__webpath=context['webpath']).first()
    if not page: return ''
    else: carousel = page.carousel    
    
    language = getattr(request, 'LANGUAGE_CODE', '')
    carousel_items = carousel.get_items(lang=language)
    data = {'carousel_items': carousel_items}
    return handle_faulty_templates(template, data, name='load_carousel')
