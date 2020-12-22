import json

from django.template import Context, Template
from django.utils.safestring import mark_safe

from cms.pages.templatetags.unicms_pages import (load_link_placeholder,
                                                 load_publication_content_placeholder)

class AbstractBlock(object):
    abtract = True

    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)
        self._rendered = False
        
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
        self.block = kwargs['block']


class PlaceHolderBlock(JSONBlock):
    """
    """
    pass


class PublicationContentPlaceholderBlock(PlaceHolderBlock):
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


class LinkPlaceholderBlock(PlaceHolderBlock):
    """
    Link PlaceHolder
    """
    def render(self):
        aspect_ratio = self.content.get('aspect_ratio', '16by9')
        template = self.content.get('template', '')
        url = self.content.get('url', None)
        if not template: return ''
        context = Context({'request': self.request,
                           'webpath': self.webpath,
                           'page': self.page,
                           'block': self})
        return load_link_placeholder(context=context,
                                     aspect_ratio=aspect_ratio,
                                     template=template,
                                     url=url)
