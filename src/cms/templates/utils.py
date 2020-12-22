import logging
import os
import re

from django.conf import settings
from django.template.backends.django import DjangoTemplates
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)
CMS_TEMPLATE_PATH_PREFIX = ''


def is_dir_usefull(dir_path):
    if os.path.isdir(dir_path) and \
       os.listdir(dir_path):
        return True


def get_unicms_templates():
    templates = []
    for te in settings.TEMPLATES:
        te['NAME'] = 'fake name'
        te.pop('BACKEND')
        td = DjangoTemplates(te)
        for dir_path in td.template_dirs:
            node = f'{dir_path}/{CMS_TEMPLATE_PATH_PREFIX}'
            if not is_dir_usefull(node): continue
            for i in ('pages', 'blocks', 'admin'):
                node2 = f'{node}{i}'
                node_els = [node, f'{i}/']
                if not is_dir_usefull(node2): continue
                if 'django/contrib/admin' in node: continue
                elements = [(node_els[0], node_els[1], e)
                            for e in os.listdir(node2)
                            if re.findall('.html$', e)]
                templates.extend(elements)
    _msg = 'uniCMS Template loader - found: {}'
    logger.debug(_msg.format(templates))
    return sorted(templates)


def import_string_block(block, request, page, webpath):
    obj = import_string(block.type)(content=block.content,
                                    request=request,
                                    page=page,
                                    webpath=webpath,
                                    block=block)
    return obj
