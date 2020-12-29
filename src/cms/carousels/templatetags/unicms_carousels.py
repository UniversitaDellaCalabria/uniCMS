import logging

from django import template

from cms.carousels.models import Carousel
from cms.contexts.utils import handle_faulty_templates
from cms.pages.models import PageCarousel

logger = logging.getLogger(__name__)
register = template.Library()


def _load_carousel_by_id(carousel_id, template,
                         func_name, lang='', log_msg=''):
    carousel = Carousel.objects.filter(carousel_id=carousel_id,
                                       is_active=True).\
                                       first()
    if not carousel:
        _msg = '{} cannot find carousel id {}'.format(log_msg,
                                                      carousel_id)
        logger.error(_msg)
        return ''

    carousel_items = carousel.get_items(lang=lang)
    data = {'carousel_items': carousel_items}
    return handle_faulty_templates(template, data, name=func_name)


@register.simple_tag(takes_context=True)
def load_carousel(context, section, template, carousel_id=None):
    _func_name = 'load_carousel'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    language = getattr(request, 'LANGUAGE_CODE', '')

    if carousel_id:
        return _load_carousel_by_id(carousel_id=carousel_id,
                                    template=template,
                                    lang=language,
                                    log_msg=_log_msg,
                                    func_name=_func_name)
    else:
        if not section: return ''
        page_carousel = PageCarousel.objects.filter(section=section,
                                                    is_active=True,
                                                    page__webpath=context['webpath']).\
                                                    first()
        if not page_carousel:
            _msg = '{} cannot find carousel in page {} and section {}'\
                   .format(log_msg, page, section)
            logger.error(_msg)
            return ''

        carousel = page_carousel.carousel
        carousel_items = carousel.get_items(lang=language)
        data = {'carousel_items': carousel_items}
        return handle_faulty_templates(template, data, name=_func_name)
