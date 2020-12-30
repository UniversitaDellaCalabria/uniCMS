import json

from django.template import Context, Template
from django.utils.safestring import mark_safe

from cms.templates.placeholders import *


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


class PlaceHolderBlock(JSONBlock):
    """
    """
    def get_template(self):
        template = self.content.get('template', '')
        return template

    def get_context(self):
        context = Context({'request': self.request,
                           'webpath': self.webpath,
                           'page': self.page,
                           'block': self})
        return context


class CarouselPlaceholderBlock(PlaceHolderBlock):
    """
    Carousel PlaceHolder
    """
    def render(self):
        template = self.get_template()
        if not template: return ''
        context = self.get_context()
        return load_carousel_placeholder(context=context,
                                         template=template)


class LinkPlaceholderBlock(PlaceHolderBlock):
    """
    Link PlaceHolder
    """
    def render(self):
        template = self.get_template()
        if not template: return ''
        context = self.get_context()
        return load_link_placeholder(context=context,
                                     template=template)


class MediaPlaceholderBlock(PlaceHolderBlock):
    """
    Media PlaceHolder
    """
    def render(self):
        template = self.get_template()
        if not template: return ''
        context = self.get_context()
        return load_media_placeholder(context=context,
                                      template=template)


class MenuPlaceholderBlock(PlaceHolderBlock):
    """
    Menu PlaceHolder
    """
    def render(self):
        template = self.get_template()
        if not template: return ''
        context = self.get_context()
        return load_menu_placeholder(context=context,
                                     template=template)


class PublicationContentPlaceholderBlock(PlaceHolderBlock):
    """
    Publication PlaceHolder
    """
    def render(self):
        template = self.get_template()
        if not template: return ''
        context = self.get_context()
        return load_publication_content_placeholder(context=context,
                                                    template=template)
