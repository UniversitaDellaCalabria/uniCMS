import datetime
import logging

from unittest import mock

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from cms.contexts import views as context_views
from cms.contexts.tests import ContextUnitTest
from cms.contexts.utils import fill_created_modified_by
from cms.medias.tests import MediaUnitTest
from cms.menus.tests import MenuUnitTest
from cms.pages.models import PageBlock, PagePublication
from cms.pages.tests import PageUnitTest
from cms.templates.blocks import PublicationContentPlaceholderBlock
from cms.templates.models import TemplateBlock
from cms.templates.tests import TemplateUnitTest

from cms.pages.templatetags.unicms_pages import cms_categories
from cms.publications.serializers import (PublicationContextSerializer,
                                          PublicationLinkSerializer,
                                          PublicationSerializer)
from cms.publications.templatetags.unicms_publications import (load_publication,
                                                               load_publications_preview)
from . import settings as app_settings
from . handlers import PublicationRssHandler
from . models import (Category, Publication, PublicationAttachment, PublicationBlock,
                      PublicationContext, PublicationMediaCollection, PublicationLink,
                      PublicationLocalization, PublicationRelated)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PublicationUnitTest(TestCase):

    def setUp(self):
        pass


    @classmethod
    def create_pub(cls, count = 4, **kwargs):
        media = MediaUnitTest.create_media()
        data = {'is_active': 1,
                'name':'my publication',
                'title':'Papiri, Codex, Libri. La attraverso labora lorem ipsum',
                'subheading':'Itaque earum rerum hic tenetur a sapiente delectus',
                'content':'<p>Sed ut <b>perspiciatis</b> unde omnis iste natus error </p>',
                'content_type': 'html',
                'presentation_image': media,
                'note':'',
                'relevance':'0',
        }
        if kwargs.get('webpath_path'):
            webpath = ContextUnitTest.create_webpath(path=kwargs.pop('webpath_path'))
        else:
            webpath = ContextUnitTest.create_webpath(path=datetime.datetime.now().strftime("%f"))
        for k,v in kwargs.items():
            data[k] = v
        category = PageUnitTest.create_category()
        for i in range(count):
            obj = Publication.objects.create(**data)
            obj.__str__()
            obj.tags.add('ciao')

            obj.category.add(category)
            ploc = PublicationLocalization.objects.create(publication=obj,
                                                          language='en',
                                                          title=f'pub eng',
                                                          subheading='',
                                                          content='',
                                                          is_active=1)
            ploc.__str__()

            # PublicationContext - related webpath
            pubcont = PublicationContext.objects.create(publication=obj,
                                                        webpath=webpath,
                                                        date_start=timezone.localtime(),
                                                        date_end=timezone.localtime() + timezone.timedelta(hours=1),
                                                        is_active=1)
        return obj


    @classmethod
    def enrich_pub(cls, **kwargs):
        pub = cls.create_pub(**kwargs)

        pub.categories
        pub.serialize()

        pub.active_translations()
        pub.image_url()

        # related pub
        pubrel = PublicationRelated.objects.create(publication=pub,
                                                   related=pub,
                                                   is_active=1)
        pubrel.__str__()
        pub.related_publications

        pubcont = pub.get_publication_context()
        webpath = pubcont.webpath

        pubcont.get_url_list(category_name='main')
        pubcont.name
        pubcont.path_prefix
        pubcont.url
        pubcont.name
        pubcont.translate_as('en')
        pubcont.serialize()
        pubcont.__str__()
        # end PubblicationContext

        pub.related_contexts
        pub.first_available_url

        # pub links
        publink = PublicationLink.objects.create(publication=pub,
                                                 name='that name',
                                                 url='https://example.org')
        publink.__str__()
        pub.related_links
        pub.related_embedded_links
        pub.related_plain_links

        # pub media collection
        media_col = MediaUnitTest.create_media_collection()

        pubga = PublicationMediaCollection.objects.create(publication = pub,
                                                          collection = media_col,
                                                          is_active=1)
        pubga.__str__()
        pub.related_media_collections

        # pub loc
        pub.translate_as(lang='en')
        pub.available_in_languages

        # test slug pre pop
        pub.save()

        # pub attachments
        data = {'publication': pub,
                'file': f'{settings.MEDIA_ROOT}/images/categories/eventi.jpg',
                'description': 'blah blah',
                'is_active': 1
        }
        pubatt = PublicationAttachment.objects.create(**data)
        pubatt.__str__()
        pub.get_attachments
        pub.get_embedded_attachments
        pub.get_plain_attachments

        # pub context felix's
        pub.url(webpath=webpath)
        pub.get_url_list(webpath=webpath)
        pub.get_publication_context(webpath=webpath)

        # PublicationBlock
        pubblock = PublicationBlock.objects.create(
                        block = TemplateUnitTest.create_block_template(),
                        publication = pub,
                        is_active = True
        )
        pubblock.__str__()
        return pub


    def test_publication_content_type(self):
        pub = self.create_pub()

        # html to markdown
        pub.content_type = 'markdown'
        pub.save()
        pub.html_content
        pub.refresh_from_db()
        assert '**' in pub.content

        # markdown to html
        pub.content_type = 'html'
        pub.save()
        pub.html_content
        pub.refresh_from_db()
        assert '</strong>' in pub.content

        # html to markdown
        pub.content_type = 'markdown'
        pub.save()
        pub.refresh_from_db()
        assert '**' in pub.content

        assert '</p>' in pub.html_content

    def test_api_pubcont(self):

        def test_call(url):
            req = Client()
            res = req.get(url).json()
            assert len(res['results']) == 4
            assert res['total_pages'] == 1
            assert res['per_page'] == 10
            assert res['count'] == 4
            assert res['page'] == 1
            assert res['previous'] == None
            assert res['next'] == None

        pub = self.create_pub()
        webpath = pub.get_publication_context().webpath
        url = reverse('unicms_api:api-news-by-contexts',
                      kwargs={'webpath_id': webpath.pk})
        test_call(url)

        url = reverse('unicms_api:api-news-by-contexts-category',
                      kwargs={'webpath_id': webpath.pk,
                              'category': 1})
        # test_call(url)

        # test next page
        # url = reverse('unicms_api:api-news-by-contexts',
                      # kwargs={'webpath_id': webpath.pk})+'?page_number=2'
        # req = Client()
        # res = req.get(url).json()
        # assert len(res['results']) == 1
        # assert res['total_pages'] == 2
        # assert res['total'] == 4
        # assert res['count'] == 1
        # assert res['page_number'] == 2
        # assert res['current_url'] == url
        # assert res['previous_url']
        # assert res['next_url'] == None


    def test_publication_handler_view(self):
        pub = self.enrich_pub(webpath_path='/')
        webpath=pub.related_contexts[0].webpath
        page = PageUnitTest.create_page(webpath=webpath)

        url = pub.related_contexts[0].url
        req = Client(HTTP_HOST='example.org')

        # privileged users avoids cache!
        user = ContextUnitTest.create_user(is_staff=1)
        req.force_login(user)

        res = req.get(url)
        assert res.status_code == 200


    def test_publication_handler_list(self):
        pub = self.enrich_pub(webpath_path='/')
        webpath=pub.related_contexts[0].webpath
        page = PageUnitTest.create_page(webpath=webpath)
        req = Client(HTTP_HOST='example.org')
        user = ContextUnitTest.create_user(is_staff=1)
        req.force_login(user)
        url = reverse('unicms:cms_dispatch')
        lurl = f'{url}{settings.CMS_PUBLICATION_LIST_PREFIX_PATH}/'
        res = req.get(lurl)
        assert res.status_code == 200


    def test_api_menu_builder_with_publications(self):
        pub = self.enrich_pub()
        webpath = pub.related_contexts[0].webpath
        # menu item that refers to a publication in a webpath
        menu = MenuUnitTest.create_menu_item(url='',
                                             publication=pub,
                                             webpath=webpath).menu

        req = Client()
        url = reverse('unicms_api:api-menu', kwargs={'menu_id': menu.pk})
        res = req.get(url, content_type='application/json')
        assert res.status_code == 200
        menu_json = res.json()
        assert isinstance(menu_json, dict)
        item = menu_json['childs'][0]
        assert item['publication_id'] == pub.pk
        assert item['webpath_id'] == webpath.pk

        # destroy the menu
        menu.delete()

        # check that it doesn't exist anymore
        res = req.get(url, content_type='application/json')
        assert res.status_code == 404


    # teamplatetags
    def test_load_publications_preview(self):
        req = RequestFactory().get('/')
        pub = self.enrich_pub()
        webpath=pub.related_contexts[0].webpath
        page = PageUnitTest.create_page(webpath=webpath)
        template_context = dict(request=req,
                                page=page, webpath=page.webpath)
        data = dict(context=template_context,
                    template='that.html',
                    exclude_negative_order=True)

        lm = load_publications_preview(**data)
        assert lm

        data['section'] = 'not-existent-section'
        lm = load_publications_preview(**data)
        assert not lm

        data['categories_csv'] = 'ciao,mamma'
        lm = load_publications_preview(**data)
        assert not lm

        data['exclude_categories'] = True
        lm = load_publications_preview(**data)
        assert not lm

        data['tags_csv'] = 'ciao,mamma'
        lm = load_publications_preview(**data)
        assert not lm

        data['in_evidence'] = True
        lm = load_publications_preview(**data)
        assert not lm


    # templatetag
    def test_load_publication(self):
        req = RequestFactory().get('/')
        pub = self.enrich_pub()
        webpath=pub.related_contexts[0].webpath
        page = PageUnitTest.create_page(webpath=webpath)
        template_context = dict(request=req,
                                page=page, webpath=page.webpath)

        data = dict(context=template_context,
                    template='that.html', publication_id=pub.pk)

        lm = load_publication(**data)
        assert lm

        # not existent pub
        data['publication_id'] = 100

        lm = load_publication(**data)
        assert not lm


    # templatetag
    @classmethod
    def test_cms_categories(cls):
        cls.enrich_pub()
        lm = cms_categories()
        assert isinstance(list(lm), list) and len(lm) == 1


    def test_fill_created_modified_by(self):
        req = RequestFactory().get('/')

        req.user = AnonymousUser()

        pub = self.create_pub()
        fill_created_modified_by(req, pub)
        pub.refresh_from_db()

        assert not pub.created_by
        assert not pub.modified_by

        req.user = ContextUnitTest.create_user(is_staff=1)
        fill_created_modified_by(req, pub)
        pub.save()
        pub.refresh_from_db()

        assert pub.created_by
        assert pub.modified_by


    # placeholders
    def test_load_publication_content_placeholder(self):
        req = RequestFactory().get('/')
        pub = self.enrich_pub()
        webpath=pub.related_contexts[0].webpath
        page = PageUnitTest.create_page(webpath=webpath)
        req = RequestFactory().get('/')

        pagepub = PagePublication.objects.create(page=page, publication=pub, is_active=1)
        pagepub.__str__()

        block = PublicationContentPlaceholderBlock(
            request = req,
            webpath = webpath,
            page = page,
            content = '{"template": "ph_publication_style_1.html"}'
        )

        template_block = TemplateBlock.objects.create(
            name = 'publication test',
            type = 'cms.templates.blocks.PublicationContentPlaceholderBlock',
            is_active = True
        )
        page_block = PageBlock.objects.create(page=page,
                                              block = template_block,
                                              is_active=1)
        lm = block.render()
        assert lm


    def test_publication_images(self):
        pub = self.create_pub(count=1)
        media = pub.presentation_image
        category = pub.category.first()

        # presentation image only
        assert pub.image_url() == media.get_media_path()
        assert pub.image_title() == media.title
        assert pub.image_description() == media.description

        # preview image has priority
        preview = MediaUnitTest.create_media(title='preview',
                                             description='preview desc')
        pub.preview_image = preview
        pub.save()
        assert pub.image_url() == preview.get_media_path()
        assert pub.image_title() == 'preview'
        assert pub.image_description() == 'preview desc'
        # serializer exposes the preview image data
        data = PublicationSerializer(pub).data
        assert data['preview_image']['title'] == 'preview'
        assert data['image'] == preview.get_media_path()
        # editorial board notes are hidden without a staff request
        assert 'note' not in data

        # no images: fallback on category image and publication texts
        pub.preview_image = None
        pub.presentation_image = None
        pub.save()
        assert str(category.image) in pub.image_url()
        assert pub.image_title() == pub.title
        assert pub.image_description() == pub.subheading

        # no images and no category images
        Category.objects.filter(pk=category.pk).update(image='')
        assert pub.image_url() is None

    def test_category_image_as_html(self):
        category = PageUnitTest.create_category()
        html = category.image_as_html()
        assert html.startswith('<img ')
        assert category.image.url in html

        # without image a placeholder path is returned
        category.image = None
        html = category.image_as_html()
        assert html == f'{settings.STATIC_URL}images/no-image.jpg'

    def test_publication_permissions(self):
        pub = self.enrich_pub()
        pub_ctx = pub.get_publication_context()
        localization = pub.publicationlocalization_set.first()
        link = pub.related_links[0]

        user = ContextUnitTest.create_user(username='simple', is_staff=True)
        superuser = ContextUnitTest.create_user(username='admin',
                                                is_staff=True,
                                                is_superuser=True)

        assert pub.is_publicable
        pub.is_active = False
        assert not pub.is_publicable

        # without user nothing is editable
        assert not pub.is_editable_by()

        # simple staff user
        assert not pub.is_lockable_by(user)
        assert not link.is_lockable_by(user)
        assert not localization.is_lockable_by(user)
        assert not pub_ctx.is_lockable_by(user)

        # superuser
        assert pub.is_lockable_by(superuser)
        assert link.is_lockable_by(superuser)
        assert localization.is_lockable_by(superuser)
        assert pub_ctx.is_lockable_by(superuser)

    def test_publication_context_status(self):
        pub = self.create_pub(count=1)
        pub_ctx = pub.get_publication_context()
        assert pub_ctx.get_absolute_url() == pub_ctx.url
        assert pub_ctx.is_published

        # expired
        pub_ctx.date_end = timezone.localtime() - timezone.timedelta(hours=1)
        assert not pub_ctx.is_published
        # not yet started
        pub_ctx.date_start = timezone.localtime() + timezone.timedelta(hours=1)
        pub_ctx.date_end = timezone.localtime() + timezone.timedelta(hours=2)
        assert not pub_ctx.is_published

    def test_foreign_key_fields_without_request(self):
        # without a request in context the related querysets are not available
        assert PublicationLinkSerializer().fields['publication'].get_queryset() is None
        assert PublicationContextSerializer().fields['webpath'].get_queryset() is None

    def test_load_publications_preview_number(self):
        req = RequestFactory().get('/')
        pub = self.create_pub()
        webpath = pub.related_contexts[0].webpath
        page = PageUnitTest.create_page(webpath=webpath)
        template_context = dict(request=req, page=page, webpath=webpath)
        data = dict(context=template_context, template='that.html')
        tag_module = 'cms.publications.templatetags.unicms_publications'
        with mock.patch(f'{tag_module}.handle_faulty_templates') as render:
            # all the 4 publications
            load_publications_preview(**data)
            assert len(render.call_args.args[1]['publications']) == 4
            # limited number of publications
            load_publications_preview(number=2, **data)
            assert len(render.call_args.args[1]['publications']) == 2

    @staticmethod
    def _rss_handler():
        """
        RSS handler is not registered in every settings.CMS_APP_REGEXP_URLPATHS
        (eg: settingslocal_example.py): register it with its default regexp
        """
        handlers = dict(context_views.CMS_APP_REGEXP_URLPATHS_LOADED)
        handlers[PublicationRssHandler] = app_settings.CMS_PUBLICATION_URL_RSS_REGEXP
        return mock.patch.object(context_views,
                                 'CMS_APP_REGEXP_URLPATHS_LOADED',
                                 handlers)

    def _staff_client(self):
        req = Client(HTTP_HOST='example.org')
        # privileged users avoids cache!
        user = ContextUnitTest.create_user(username='staff-handler',
                                           is_staff=1)
        req.force_login(user)
        return req

    def test_publication_handler_view_not_found(self):
        pub = self.enrich_pub(webpath_path='/')
        webpath = pub.related_contexts[0].webpath
        PageUnitTest.create_page(webpath=webpath)
        req = self._staff_client()

        url = pub.related_contexts[0].url
        res = req.get(url)
        assert res.status_code == 200
        assert pub.title in res.content.decode()

        # not existent publication in webpath
        url = url.replace(f'/{pub.pk}-', f'/{pub.pk + 100}-')
        res = req.get(url)
        assert res.status_code == 404

    def test_publication_handler_list_category(self):
        pub = self.enrich_pub(webpath_path='/')
        webpath = pub.related_contexts[0].webpath
        PageUnitTest.create_page(webpath=webpath)
        category = pub.category.first()
        req = self._staff_client()
        lurl = f'{webpath.get_full_path()}{settings.CMS_PUBLICATION_LIST_PREFIX_PATH}/'

        res = req.get(lurl, {'category_name': category.name.upper()})
        assert res.status_code == 200
        assert f'category={category.pk}' in res.content.decode()

        # unknown category: no filter
        res = req.get(lurl, {'category_name': 'not-existent'})
        assert res.status_code == 200
        assert 'category=' not in res.content.decode()

    def test_publication_handler_list_without_page(self):
        pub = self.create_pub(webpath_path='/')
        webpath = pub.related_contexts[0].webpath
        req = self._staff_client()
        lurl = f'{webpath.get_full_path()}{settings.CMS_PUBLICATION_LIST_PREFIX_PATH}/'
        res = req.get(lurl)
        assert res.status_code == 404

        rss_url = f'{webpath.get_full_path()}{app_settings.CMS_PUBLICATION_RSS_PREFIX_PATH}/'
        with self._rss_handler():
            res = req.get(rss_url)
        assert res.status_code == 404

    def test_publication_handler_rss(self):
        pub = self.create_pub(count=2, webpath_path='/')
        webpath = pub.related_contexts[0].webpath
        PageUnitTest.create_page(webpath=webpath)
        pub_ctxs = list(PublicationContext.objects.filter(webpath=webpath))
        empty_pub = pub_ctxs[0].publication
        full_pub = pub_ctxs[1].publication
        # no translations: contents are deterministic
        PublicationLocalization.objects.filter(publication__in=(empty_pub, full_pub)).delete()
        Publication.objects.filter(pk=empty_pub.pk).update(title='empty pub',
                                                           content='')
        Publication.objects.filter(pk=full_pub.pk).update(title='full pub',
                                                          content='<p>rss body</p>')
        category = full_pub.category.first()

        req = self._staff_client()
        patcher = self._rss_handler()
        patcher.start()
        self.addCleanup(patcher.stop)
        url = f'{webpath.get_full_path()}{app_settings.CMS_PUBLICATION_RSS_PREFIX_PATH}/'
        res = req.get(url, HTTP_ACCEPT_LANGUAGE='en')
        assert res.status_code == 200
        assert 'rss' in res['Content-Type']
        content = res.content.decode()
        assert 'xmlns:content="http://purl.org/rss/1.0/modules/content/"' in content
        assert content.count('<item>') == 2
        assert '<title>empty pub</title>' in content
        assert '<title>full pub</title>' in content
        assert '<content:encoded/>' in content
        assert '<content:encoded><![CDATA[<p>rss body</p>]]></content:encoded>' in content
        assert f'<category>{category.name}</category>' in content
        assert f'<description>{full_pub.subheading}</description>' in content
        assert '<pubDate>' in content

        # category filter
        res = req.get(url, {'category_name': category.name.upper()})
        assert res.content.decode().count('<item>') == 2
        res = req.get(url, {'category_name': 'not-existent'})
        assert res.status_code == 200
        assert '<item>' not in res.content.decode()
