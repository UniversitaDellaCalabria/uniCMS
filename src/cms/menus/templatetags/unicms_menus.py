import logging

from django import template
from django.template.exceptions import (TemplateDoesNotExist,
                                        TemplateSyntaxError)
from django.utils import timezone
from cms.contexts.utils import handle_faulty_templates
from cms.menus.models import NavigationBar
from cms.pages.models import PageMenu, Page

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag(takes_context=True)
def load_menu(context, template, section=None, menu_id=None):
    request = context['request']
    language = getattr(request, 'LANGUAGE_CODE', '')

    if menu_id:
        menu = NavigationBar.objects.filter(pk=menu_id,
                                            is_active=True).\
                                            first()
        if not menu: return ''
        items = menu.get_items(lang=language, parent__isnull=True)
        data = {'items': items}
        return handle_faulty_templates(template, data, name='load_menu')

    else:
        if not section: return ''
        # draft mode
        if request.session.get('draft_view_mode'):
            page = Page.objects.filter(webpath = context['webpath'],
                                       is_active = True)
            page = page.filter(state = 'draft').last() or context['page']
        else:
            page = context['page']
        page_menu = PageMenu.objects.filter(section=section,
                                            is_active=True,
                                            page=page).first()
        if not page_menu: return ''
        items = page_menu.menu.get_items(lang=language,
                                         parent__isnull=True)
        data = {'items': items}
        return handle_faulty_templates(template, data, name='load_menu')
