import logging

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.safestring import SafeString

from cms.contexts.decorators import detect_language
from cms.contexts.utils import handle_faulty_templates
from cms.pages.models import Category
from cms.publications.models import PublicationContext


logger = logging.getLogger(__name__)
register = template.Library()


def _get_pub_qparams(context, webpath, section = None, in_evidence=False,
                     categories_csv=None, tags_csv=None):
    now = timezone.localtime()    
    query_params = dict(webpath=context['webpath'],
                        is_active=True,
                        publication__is_active=True,
                        publication__date_start__lte=now,
                        publication__state="published")
    if section:
        query_params['section'] = section
    if in_evidence:
        query_params['in_evidence_start__lte'] = now
        query_params['in_evidence_start__gt'] = now
    if categories_csv:
        cats = [i.strip() for i in categories_csv.split(',')]
        query_params['publication__category__name__in'] = cats
    if tags_csv:
        tags = [i.strip() for i in tags_csv.split(',')]
        query_params['publication__tags__name__in'] = tags
    
    return query_params


@register.simple_tag(takes_context=True)
def load_publications_preview(context, template,
                              section = None,
                              number=5,
                              in_evidence=False,
                              categories_csv=None, tags_csv=None):
    request = context['request']
    webpath = context['webpath']
    query_params = _get_pub_qparams(context = context ,
                                    webpath=webpath, 
                                    section = section,
                                    in_evidence = in_evidence,
                                    categories_csv = categories_csv,
                                    tags_csv = tags_csv)

    pub_in_context = PublicationContext.objects.\
                        filter(**query_params).\
                        order_by('order')[0:number]

    if not pub_in_context: return ''

    # i18n
    language = getattr(request, 'LANGUAGE_CODE', '')
    for i in pub_in_context:
        i.publication.translate_as(lang=language)

    data = {'publications': pub_in_context}
    return handle_faulty_templates(template, data,
                                   name='load_publications_preview')


@register.simple_tag(takes_context=True)
def load_publication_content_placeholder(context, template,
                                         section = None,
                                         publication_id = None):
    # i18n
    language = getattr(request, 'LANGUAGE_CODE', '')
    _func_name = 'load_publication_content_placeholder'
    _log_msg = f'Template Tag {_func_name}'
    
    request = context['request']
    webpath = context['webpath']
    block = context.get('block')
    page = context['page']
    if not block:
        logger.warning(f'{_func_name} cannot get a block object')
        return ''
    
    # id is quite arbitrary
    if publication_id:
        pub = Publication.objects.filter(pk = publication_id).first()
        
        if not pub:
            _msg = '{} cannot find publication id {}'.format(_log_msg, 
                                                             publication_id)
            logger.error(_msg)
            return ''
        
        pub.translate_as(lang=language)
        data = {'publication': pub}
        return handle_faulty_templates(template, data, name=_func_name)
        
    else:
        pubs = page.pagepublication_set.filter(page=page, 
                                               in_active=True).\
                                        order_by('order')
        for i in pubs:
            i.translate_as(lang=language)
        
        if not ph:
            _msg = '{} doesn\'t have any page publications'.format(_log_msg)
            logger.warning(_msg)
            return ''
        
        blocks = page.get_blocks()
        ph = [i for i in blocks
              if blocks.type == \
              'cms.templates.blocks.PublicationContentPlaceholderBlock']
        
        for i in zip(ph, pubs):
            if i[0] == block:
                data = {'publication': i[1]}
                return handle_faulty_templates(template, data, name=_func_name)
    
    
    
