from django.conf import settings
from django.contrib.syndication.views import Feed
from django.http import (HttpResponse,
                         Http404)
from django.db.models import Q
from django.template import Template, Context
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
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
                          publication__pk=self.match_dict.get('id', ''),
                          publication__slug=self.match_dict.get('slug', ''),
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


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    """
    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        # Because I'm adding a <content:encoded> field, I first need to declare
        # the content namespace. For more information on how this works, check
        # out: http://validator.w3.org/feed/docs/howto/declare_namespaces.html
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs

    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)

        if item['content_encoded']:
            content = f"<content:encoded><![CDATA[{item['content_encoded']}]]></content:encoded>"
        else:
            content = "<content:encoded/>"
        handler._write(content)


class PublicationRssHandler(BaseContentHandler, Feed):
    feed_type = ExtendedRSSFeed
    # description_template = 'feeds/list_detail_content_encoded.html'

    def items(self):
        query_params = publication_context_base_filter()
        query_categories = Q()
        category_name = self.request.GET.get('category_name')
        if category_name:
            query_category = Q(publication__category__name__iexact=category_name)
        items = PublicationContext.objects\
                                  .filter(query_category,
                                          webpath=self.page.webpath,
                                          **query_params)\
                                  .select_related('publication')[:10]

        # i18n
        lang = getattr(self.request, 'LANGUAGE_CODE', None)
        if lang:
            for item in items:
                item.publication.translate_as(lang=lang)
        return items

    def item_title(self, item):
        return item.publication.title

    def item_description(self, item):
        return item.publication.subheading

    # def item_author_name(self, item):
        # if (item.author.get_full_name()):
            # return item.author.get_full_name()
        # else:
            # return item.author

    def item_pubdate(self, item):
        return item.date_start

    def item_categories(self, item):
        return item.publication.categories.values_list('name', flat=True)

    def item_content_encoded(self, item):
        return item.publication.content

    def item_extra_kwargs(self, item):
        return {'content_encoded': self.item_content_encoded(item)}

    def as_view(self):
        match_dict = self.match.groupdict()
        self.page = Page.objects.filter(is_active=True,
                                   webpath__site=self.website,
                                   webpath__fullpath=match_dict.get('webpath', '/'))\
                                .select_related('webpath','webpath__site').first()

        if not self.page:
            raise Http404()

        self.title = f'{self.page.webpath.name} - {self.page.webpath.site.name}'
        self.link = f"{self.page.webpath.fullpath}{CMS_PUBLICATION_LIST_PREFIX_PATH}"
        self.description = f"{self.page.webpath.name} RSS feed"

        response = self.__call__(request=self.request)
        return response
