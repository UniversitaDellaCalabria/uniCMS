import json

from django.template import Context, Template
from django.utils.safestring import mark_safe

from cms.publications.templatetags.unicms_publications import load_publication_content_placeholder


class AbstractBlock(object):
    abtract = True

    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

    def render(self):
        return mark_safe(self.content)


class HtmlBlock(AbstractBlock):
    def render(self):
        template = Template(self.content)
        context = Context({'request': self.request,
                           'webpath': self.webpath,
                           'page': self.page,
                           'block': self})
        return template.render(context)


class JSONBlock(AbstractBlock):
    def __init__(self, content='', **kwargs):
        self.content = json.loads(content)
        self.request = kwargs['request']
        self.webpath = kwargs['webpath']
        self.page = kwargs['page']


class PublicationContentPlaceholderBlock(JSONBlock):
    """
    Publication PlaceHolder
    """
    def render(self):
        template = self.content.get('template', '')
        publication_id = self.content.get('publication_id', None)
        if not template: return ''
        context = Context({'request': self.request,
                           'webpath': self.webpath,
                           'page': self.page,
                           'block': self})
        return load_publication_content_placeholder(context=context,
                                                    publication_id=publication_id,
                                                    template=template)
