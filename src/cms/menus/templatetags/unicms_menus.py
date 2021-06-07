import logging

from django import template
from django.conf import settings
from django.utils.safestring import SafeString

from cms.contexts.utils import handle_faulty_templates, append_slash
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


@register.simple_tag(takes_context=True)
def load_item_childs(context, item):
    _func_name = 'load_item_childs'
    _log_msg = f'Template Tag {_func_name}'

    if item:
        request = context['request']
        language = getattr(request, 'LANGUAGE_CODE', '')

        return item.get_childs(lang=language)


@register.simple_tag(takes_context=True)
def load_item_inherited_content(context, item):
    _func_name = 'load_item_inherited_content'
    _log_msg = f'Template Tag {_func_name}'

    if item and item.inherited_content and item.inherited_content.is_active:
        request = context['request']
        language = getattr(request, 'LANGUAGE_CODE', '')
        item.inherited_content.translate_as(lang=language)
        return item.inherited_content


@register.simple_tag(takes_context=True)
def load_item_publication(context, item):
    _func_name = 'load_item_publication'
    _log_msg = f'Template Tag {_func_name}'

    if item and item.publication and item.publication.is_active:
        request = context['request']
        language = getattr(request, 'LANGUAGE_CODE', '')
        item.publication.translate_as(lang=language)
        return item.publication


def _get_current_item(item, path, language):
    webpath = item.webpath
    if webpath and not webpath.is_alias:
        if path == webpath.get_full_path():
            return item
    for child in item.get_childs():
        result = _get_current_item(child, path, language)
        if result: return result
    return None # pragma: no cover


@register.simple_tag(takes_context=True)
def load_current_item_from_menu(context):
    _func_name = 'load_current_item_from_menu'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    language = getattr(request, 'LANGUAGE_CODE', '')

    path = append_slash(request.path)

    for item in context['items']:
        result = _get_current_item(item, path, language)
        if result: return result


def _get_others_same_level_items(item, path, language):
    webpath = item.webpath
    if webpath and not webpath.is_alias:
        if path == webpath.get_full_path():
            parent = item.parent
            if parent:
                return {'parent': parent.localized(lang=language),
                        'items': parent.get_childs(lang=language, exclude=item)}
    for child in item.get_childs():
        result = _get_others_same_level_items(child, path, language)
        if result: return result
    return {} # pragma: no cover


@register.simple_tag(takes_context=True)
def load_other_items_from_menu(context):
    _func_name = 'load_other_items_from_menu'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    language = getattr(request, 'LANGUAGE_CODE', '')

    path = append_slash(request.path)

    for item in context['items']:
        result = _get_others_same_level_items(item, path, language)
        if result: return result
