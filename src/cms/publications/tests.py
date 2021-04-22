import datetime
import logging

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

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
from cms.publications.templatetags.unicms_publications import (load_publication,
                                                               load_publications_preview)
from . models import (Publication, PublicationAttachment, PublicationBlock,
                      PublicationContext, PublicationGallery, PublicationLink,
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

        # pub gallery
        media_col = MediaUnitTest.create_media_collection()

        pubga = PublicationGallery.objects.create(publication = pub,
                                                  collection = media_col,
                                                  is_active=1)
        pubga.__str__()
        pub.related_galleries

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
        pub.get_attachments()

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
            assert len(res['results']) == 3
            assert res['total_pages'] == 2
            assert res['total'] == 4
            assert res['count'] == 3
            assert res['page_number'] == 1
            assert res['current_url'] == url
            assert res['previous_url'] == None
            assert res['next_url']

        pub = self.create_pub()
        webpath = pub.get_publication_context().webpath
        url = reverse('unicms_api:api-news-by-contexts',
                      kwargs={'webpath_id': webpath.pk})
        test_call(url)

        url = reverse('unicms_api:api-news-by-contexts-category',
                      kwargs={'webpath_id': webpath.pk,
                              'category_name': 'main'})
        test_call(url)

        # test next page
        url = reverse('unicms_api:api-news-by-contexts',
                      kwargs={'webpath_id': webpath.pk})+'?page_number=2'
        req = Client()
        res = req.get(url).json()
        assert len(res['results']) == 1
        assert res['total_pages'] == 2
        assert res['total'] == 4
        assert res['count'] == 1
        assert res['page_number'] == 2
        assert res['current_url'] == url
        assert res['previous_url']
        assert res['next_url'] == None


    def test_api_pub_detail(self):
        pub = self.enrich_pub()
        req = Client()
        url = reverse('unicms_api:publication-detail',
                      kwargs={'slug': pub.slug})
        req.get(url).json()


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
        lurl = f'{url}{settings.CMS_PUBLICATION_LIST_PREFIX_PATH}'
        res = req.get(lurl)
        assert res.status_code == 200


    def test_api_menu_builder_with_publications(self):
        pub = self.enrich_pub()
        webpath = pub.related_contexts[0].webpath
        menu = MenuUnitTest.create_menu_item().menu

        req = Client()
        url = reverse('unicms_api:api-menu', kwargs={'menu_id': 1})
        res = req.get(url, content_type='application/json')
        assert isinstance(res.json(), dict)

        menu_json = res.json()
        # destroy the menu
        menu.delete()

        # check that it doesn't exist anymore
        res = req.get(url, content_type='application/json')
        assert res.status_code == 404

        # re-create the menu - with unprivileged user
        url = reverse('unicms_api:api-menu-post')
        res = req.post(url, data=menu_json,
                       content_type='application/json', follow=1)
        assert res.status_code == 403

        # re-create the menu - with privileged user
        user = ContextUnitTest.create_user(is_staff=1)
        req.force_login(user)

        url = reverse('unicms_api:api-menu-post')
        res = req.post(url, data=menu_json,
                       content_type='application/json', follow=1)

        menu_item = {'parent_id': None,
                     'name': 'Other',
                     'url': '',
                     'publication_id': 1,
                     'webpath_id': webpath.pk,
                     'is_active': True,
                     'order': 10,
                     'childs': []}
        menu_item['childs'] = [menu_item.copy()]

        # update a menu
        menu_json['childs'].append(menu_item)
        menu_json['childs'][-1]['publication_id'] = None

        # not existing menu
        url = reverse('unicms_api:api-menu', kwargs={'menu_id': 100})
        res = req.post(url, data=menu_json,
                      content_type='application/json', follow=1)
        assert res.status_code == 404

        # update a menu
        url = reverse('unicms_api:api-menu', kwargs={'menu_id': 2})
        res = req.post(url, data=menu_json,
                      content_type='application/json', follow=1)
        # verify
        res = req.get(url, content_type='application/json')
        assert len(res.json()['childs']) == 2
        logger.debug(res.json())


    # teamplatetags
    def test_load_publications_preview(self):
        req = RequestFactory().get('/')
        pub = self.enrich_pub()
        webpath=pub.related_contexts[0].webpath
        page = PageUnitTest.create_page(webpath=webpath)
        template_context = dict(request=req,
                                page=page, webpath=page.webpath)
        data = dict(context=template_context, template='that.html')

        lm = load_publications_preview(**data)
        assert lm

        data['section'] = 'not-existent-section'
        lm = load_publications_preview(**data)
        assert not lm

        data['categories_csv'] = 'ciao,mamma'
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
