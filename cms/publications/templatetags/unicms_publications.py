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


@register.simple_tag(takes_context=True)
def load_publications_preview(context, template,
                              section = None,
                              number=5,
                              in_evidence=False,
                              categories_csv=None, tags_csv=None):
    request = context['request']
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
