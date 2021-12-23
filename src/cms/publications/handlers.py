from django.conf import settings
from django.http import (HttpResponse,
                         Http404)
from django.template import Template, Context
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from cms.contexts.handlers import BaseContentHandler
from cms.contexts.utils import contextualize_template, sanitize_path
from cms.pages.models import Page

from . models import Category, PublicationContext
from . settings import CMS_PUBLICATION_LIST_PREFIX_PATH, CMS_PAGE_SIZE
from . utils import publication_context_base_filter


PAGE_SIZE = getattr(settings, 'CMS_PAGE_SIZE', CMS_PAGE_SIZE)


class PublicationViewHandler(BaseContentHandler):
    template = "publication_view.html"

    def __init__(self, **kwargs):
        super(PublicationViewHandler, self).__init__(**kwargs)
        self.match_dict = self.match.groupdict()
        query = publication_context_base_filter()
        query.update(dict(webpath__site=self.website,
                          webpath__fullpath=self.match_dict.get('webpath', '/'),
                          publication__slug=self.match_dict.get('slug', '')
                    )
        )
        self.pub_context = PublicationContext.objects.filter(**query).first()
        if not hasattr(self.pub_context, 'webpath'): # pragma: no cover
            raise Http404('Unknown WebPath')

        self.page = Page.objects.filter(is_active=True,
                                        webpath=self.pub_context.webpath).first()
        self.webpath = self.pub_context.webpath

    def as_view(self):
        if not self.pub_context: return Http404()

        # i18n
        lang = getattr(self.request, 'LANGUAGE_CODE', None)
        if lang:
            self.pub_context.publication.translate_as(lang=lang)

        data = {'request': self.request,
                'webpath': self.webpath,
                'website': self.website,
                'page': self.page,
                'path': self.match_dict.get('webpath', '/'),
                'publication_context': self.pub_context,
                'handler': self}

        ext_template_sources = contextualize_template(self.template,
                                                      self.page)
        template = Template(ext_template_sources)
        context = Context(data)
        return HttpResponse(template.render(context), status=200)

    @property
    def parent_path_prefix(self):
        return getattr(settings, 'CMS_PUBLICATION_LIST_PREFIX_PATH',
                       CMS_PUBLICATION_LIST_PREFIX_PATH)

    @property
    def parent_url(self):
        url = f'{self.webpath.get_full_path()}/{self.parent_path_prefix}/'
        return sanitize_path(url)

    @property
    def breadcrumbs(self):
        leaf = (self.pub_context.url, getattr(self.pub_context.publication, 'title'))
        parent = (self.parent_url, _('News'))
        return (parent, leaf)


class PublicationListHandler(BaseContentHandler):
    template = "publication_list.html"

    @property
    def breadcrumbs(self):
        path = self.path
        leaf = (path, _('News'))
        return (leaf,)

    def as_view(self):
        category = None
        category_name = self.request.GET.get('category_name')
        if category_name:
            category = Category.objects.filter(name__iexact=category_name).first()

        match_dict = self.match.groupdict()
        page = Page.objects.filter(is_active=True,
                                   webpath__site=self.website,
                                   webpath__fullpath=match_dict.get('webpath', '/')).first()
        if not page: # pragma: no cover
            raise Http404('Unknown Web Page')

        data = {'request': self.request,
                'webpath': page.webpath,
                'website': self.website,
                'page': page,
                'path': match_dict.get('webpath', '/'),
                'handler': self,
                'category_name': category.name if category else ''
                }

        base_url = reverse('unicms_api:api-news-by-contexts',
                            kwargs = {'webpath_id': page.webpath.pk })
        base_url = base_url + f'?page=1&page_size={PAGE_SIZE}'
        if category:
            base_url = base_url + f'&category={category.pk}'
        data['url'] = base_url

        ext_template_sources = contextualize_template(self.template, page)
        template = Template(ext_template_sources)
        context = Context(data)
        return HttpResponse(template.render(context), status=200)
