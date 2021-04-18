import logging
import re

from django.conf import settings
from django.contrib import messages
from django.utils import translation
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from django.template.loader import get_template, render_to_string
from django.template.exceptions import (TemplateDoesNotExist,
                                        TemplateSyntaxError)

logger = logging.getLogger(__name__)
CMS_PATH_PREFIX = getattr(settings, 'CMS_PATH_PREFIX', '')


def get_CMS_HOOKS():
    return {k:{kk:[import_string(i) for i in vv] for kk,vv in v.items()}
            for k,v in getattr(settings, 'CMS_HOOKS', {}).items()}


def detect_user_language(request):
    lang = request.GET.get('lang',
                           translation.get_language_from_request(request))
    translation.activate(lang)
    request.LANGUAGE_CODE = translation.get_language()
    return lang


def handle_faulty_templates(template: str, data: dict, name='', ): # pragma: no cover
    _error_msg = 'ERROR: {} template tags: {}'
    _error_msg_pub = '<!-- Error {} template tags. See log file. -->'

    try:
        return render_to_string(template, data)
    except TemplateDoesNotExist as e:
        logger.error(_error_msg.format(name, e))
    except TemplateSyntaxError as e:
        logger.error(_error_msg.format(name, e))

    return mark_safe(_error_msg_pub) # nosec


def contextualize_template(template_fname, page):
    template_obj = get_template(template_fname)
    template_sources = template_obj.template.source

    # do additional preprocessing on the template here ...
    # get/extends the base template of the page context
    base_template_tag = f'{{% extends "{page.base_template.template_file}" %}}'
    regexp = r"\{\%\s*extends\s*\t*[\'\"a-zA-Z0-9\_\-\.]*\s*\%\}"
    ext_template_sources = re.sub(regexp, base_template_tag, template_sources)
    # end string processing
    return ext_template_sources


def sanitize_path(path):
    return re.sub('/[/]+', '/', path)


def append_slash(path):
    return f'{path}/' if path[-1] != '/' else path


def toggle_session_state(request, arg_name) -> None:
    state_session = request.session.get(arg_name)
    state_request = request.GET.get(arg_name, 'not-set')
    if state_request in ('1', 'true', 'True'):
        state_request = True
    elif state_request in ('0', 'false', 'False'):
        state_request = False
    elif state_request in ('', None):
        state_request = 'toggle'

    if state_request in (True, False):
        request.session[arg_name] = state_request
    elif state_request == 'toggle':
        if state_session:
            request.session[arg_name] = False
        else:
            request.session[arg_name] = True

    if state_request in (True, 'toggle') and request.session[arg_name]:
        messages.add_message(request, messages.INFO,
                             _('You entered in {}').format(arg_name.upper()))


def load_hooks(obj, flow_type, *args, **kwargs):
    _msg_hook_exp = '{} Hook {} failed with: {}'
    type_hooks = get_CMS_HOOKS().get(obj.__class__.__name__, {})
    flow_hooks = type_hooks.get(flow_type, [])

    # pre-Save HOOKS call
    for hook in flow_hooks:
        try:
            hook(obj)
        except Exception as e: # pragma: no cover
            logger.exception(_msg_hook_exp.format(flow_type, hook, e))


def fill_created_modified_by(request, obj):
    if not request.user.is_authenticated:
        return False

    for field_name in ('created_by', 'modified_by'):
        if not hasattr(obj, field_name):# pragma: no cover
            continue

        if (field_name == 'modified_by' or not getattr(obj, field_name, None)):
            setattr(obj, field_name, request.user)


def is_translator(permission):
    """
    based on settings.CMS_CONTEXT_PERMISSIONS
    given a permission code (int)
    returns a dict{} with translator permission info
    """
    if not permission > 0: return {}
    allow_descendant = True if permission > 1 else False
    return {'only_created_by': False,
            'allow_descendant': allow_descendant}


def is_editor(permission):
    """
    based on settings.CMS_CONTEXT_PERMISSIONS
    given a permission code (int)
    returns a dict{} with editor permission info
    """
    if not permission > 2: return {}
    allow_descendant = True if permission > 4 else False
    only_created_by = True if permission == 3 else False
    return {'only_created_by': only_created_by,
            'allow_descendant': allow_descendant}


def is_publisher(permission):
    """
    based on settings.CMS_CONTEXT_PERMISSIONS
    given a permission code (int)
    returns a dict{} with publiser permission info
    """
    if not permission > 5: return {}
    allow_descendant = True if permission == 7 else False
    return {'only_created_by': False,
            'allow_descendant': allow_descendant}
