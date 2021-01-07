import logging

from django import template
from django.utils.safestring import SafeString

from cms.contexts.utils import handle_faulty_templates
from cms.menus.models import NavigationBar


logger = logging.getLogger(__name__)
register = template.Library()


def _load_menu_by_id(menu_id, template,
                     func_name, lang='', log_msg=''):
    menu = NavigationBar.objects.filter(pk=menu_id,
                                        is_active=True).\
                                        first()
    if not menu:
        _msg = '{} cannot find menu id {}'.format(log_msg, menu_id)
        logger.error(_msg)
        return SafeString('')

    items = menu.get_items(lang=lang, parent__isnull=True)
    data = {'items': items}
    return handle_faulty_templates(template, data, name=func_name)


@register.simple_tag(takes_context=True)
def load_menu(context, template, section=None, menu_id=None):
    _func_name = 'load_menu'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    language = getattr(request, 'LANGUAGE_CODE', '')

    if menu_id:
        return _load_menu_by_id(menu_id=menu_id,
                                template=template,
                                lang=language,
                                log_msg=_log_msg,
                                func_name=_func_name)
    else:
        if not section: return SafeString('')
        page = context['page']
        page_menu = page.get_menus().filter(section=section).first()
        if not page_menu:
            _msg = '{} cannot find menu in page {} and section {}'\
                   .format(_log_msg, page, section)
            logger.error(_msg)
            return SafeString('')
        items = page_menu.menu.get_items(lang=language,
                                         parent__isnull=True)
        data = {'items': items}
        return handle_faulty_templates(template, data, name=_func_name)
