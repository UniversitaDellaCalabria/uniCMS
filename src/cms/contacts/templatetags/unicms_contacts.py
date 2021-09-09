import logging

from django import template
from django.utils.safestring import SafeString

from cms.contacts.models import Contact
from cms.contexts.utils import handle_faulty_templates


logger = logging.getLogger(__name__)
register = template.Library()


def _load_contact_by_id(contact_id, template,
                        func_name, lang='', log_msg=''):
    contact = Contact.objects.filter(pk=contact_id,
                                     is_active=True).\
                                     first()
    if not contact:
        _msg = '{} cannot find contact id {}'.format(log_msg,
                                                     contact_id)
        logger.error(_msg)
        return SafeString('')

    contact_infos = contact.get_infos(lang=lang)
    data = {'contact': contact.localized(lang=lang),
            'contact_infos': contact_infos}
    return handle_faulty_templates(template, data, name=func_name)


@register.simple_tag(takes_context=True)
def load_contact(context, section, template, contact_id=None):
    _func_name = 'load_contact'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    page = context['page']
    language = getattr(request, 'LANGUAGE_CODE', '')

    if contact_id:
        return _load_contact_by_id(contact_id=contact_id,
                                   template=template,
                                   lang=language,
                                   log_msg=_log_msg,
                                   func_name=_func_name)
    else:
        if not section: return SafeString('')

        page_contact = page.get_contacts().first()

        if not page_contact: # pragma: no cover
            _msg = '{} cannot find contact in page {} and section {}'\
                   .format(_func_name, page, section)
            logger.error(_msg)
            return SafeString('')

        contact = page_contact.contact
        contact_infos = contact.get_infos(lang=language)
        data = {'contact': contact.localized(lang=language),
                'contact_infos': contact_infos}
        return handle_faulty_templates(template, data, name=_func_name)
