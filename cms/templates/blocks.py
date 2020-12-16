import json

from django.template import Context, Template
from django.utils.safestring import mark_safe


class AbstractBlock(object):
    abtract = True

    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

    def render(self):
        return mark_safe(self.content)


class NullBlock(AbstractBlock):
    """
    clean up the inheritance from a parent page
    """
    pass


class HtmlBlock(AbstractBlock):
    def render(self):
        template = Template(self.content)
        context = Context({'request': self.request,
                           'webpath': self.webpath,
                           'page': self.page})
        return template.render(context)


class JSONBlock(AbstractBlock):
    def __init__(self, content=''):
        self.content = json.loads(content)

