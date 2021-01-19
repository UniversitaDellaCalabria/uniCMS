import logging

from django import template
from django.utils import timezone
from django.utils.safestring import SafeString

from cms.contexts.utils import handle_faulty_templates
from cms.publications.models import Publication, PublicationContext


logger = logging.getLogger(__name__)
register = template.Library()


def _get_pub_qparams(context, webpath, section = None, in_evidence=False,
                     categories_csv=None, tags_csv=None):
    now = timezone.localtime()
    query_params = dict(webpath=context['webpath'],
                        is_active=True,
                        publication__is_active=True,
                        date_start__lte=now,
                        date_end__gt=now)
    # publication__state="published")
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
def load_publication(context, template, publication_id):
    _func_name = 'load_publication'
    _log_msg = f'Template Tag {_func_name}'

    request = context['request']
    webpath = context['webpath']
    language = getattr(request, 'LANGUAGE_CODE', '')

    pub = Publication.objects.filter(pk=publication_id,
                                     is_active=True).first()

    if not pub:
        _msg = '{} cannot find publication id {}'.format(_log_msg,
                                                         publication_id)
        logger.error(_msg)
        return SafeString('')

    pub.translate_as(lang=language)
    data = {'publication': pub, 'webpath': webpath}
    return handle_faulty_templates(template, data, name=_func_name)


@register.simple_tag(takes_context=True)
def load_publications_preview(context, template,
                              section = None,
                              number=5,
                              in_evidence=False,
                              categories_csv=None, tags_csv=None):
    request = context['request']
    webpath = context['webpath']
    query_params = _get_pub_qparams(context=context ,
                                    webpath=webpath,
                                    section=section,
                                    in_evidence=in_evidence,
                                    categories_csv=categories_csv,
                                    tags_csv=tags_csv)

    pub_in_context = PublicationContext.objects.\
        filter(**query_params).\
        order_by('order')[0:number]

    if not pub_in_context: return SafeString('')

    # i18n
    language = getattr(request, 'LANGUAGE_CODE', '')
    for i in pub_in_context:
        i.publication.translate_as(lang=language)

    data = {'publications': pub_in_context}
    return handle_faulty_templates(template, data,
                                   name='load_publications_preview')
