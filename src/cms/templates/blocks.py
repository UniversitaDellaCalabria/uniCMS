import json

from django.template import Context, Template
from django.utils.safestring import mark_safe

from cms.templates.placeholders import (SafeString, load_carousel_placeholder,
                                        load_link_placeholder, load_media_placeholder,
                                        load_menu_placeholder,
                                        load_publication_content_placeholder)


class AbstractBlock(object):
    abtract = True

    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)
        self._rendered = False

    def get_context(self):
        context = Context({'request': self.request,
                           'webpath': self.webpath,
                           'page': self.page,
                           'block': self})
        return context

    def render(self): # pragma: no cover
        return mark_safe(self.content) # nosec


class HtmlBlock(AbstractBlock):
    def render(self):
        template = Template(self.content)
        context = self.get_context()
        return template.render(context)


class JSONBlock(AbstractBlock):
    def __init__(self, content='{}', **kwargs):
        super(JSONBlock, self).__init__(**kwargs)
        self.content = json.loads(content)


class PlaceHolderBlock(JSONBlock):
    """
    """

    def sanitize_template(self):
        if not self.content.get('template'):
            self.content['template'] = SafeString('')


class CarouselPlaceholderBlock(PlaceHolderBlock):
    """
    Carousel PlaceHolder
    """

    def render(self):
        self.sanitize_template()
        context = self.get_context()
        return load_carousel_placeholder(context=context,
                                         content=self.content)


class LinkPlaceholderBlock(PlaceHolderBlock):
    """
    Link PlaceHolder
    """

    def render(self):
        self.sanitize_template()
        context = self.get_context()
        return load_link_placeholder(context=context,
                                     content=self.content)


class MediaPlaceholderBlock(PlaceHolderBlock):
    """
    Media PlaceHolder
    """

    def render(self):
        self.sanitize_template()
        context = self.get_context()
        return load_media_placeholder(context=context,
                                      content=self.content)


class MenuPlaceholderBlock(PlaceHolderBlock):
    """
    Menu PlaceHolder
    """

    def render(self):
        self.sanitize_template()
        context = self.get_context()
        return load_menu_placeholder(context=context,
                                     content=self.content)


class PublicationContentPlaceholderBlock(PlaceHolderBlock):
    """
    Publication PlaceHolder
    """

    def render(self):
        self.sanitize_template()
        context = self.get_context()
        return load_publication_content_placeholder(context=context,
                                                    content=self.content)
