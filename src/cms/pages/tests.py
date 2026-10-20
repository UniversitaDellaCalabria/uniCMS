import importlib
import logging
import datetime

from django.conf import settings
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from cms.contacts.templatetags.unicms_contacts import load_contact
from cms.contacts.tests import ContactUnitTest
from cms.carousels.templatetags.unicms_carousels import load_carousel
from cms.carousels.tests import CarouselUnitTest
from cms.contexts.tests import ContextUnitTest
from cms.medias.tests import MediaUnitTest
from cms.menus.tests import MenuUnitTest
from cms.menus.templatetags.unicms_menus import *
from cms.pages.templatetags.unicms_pages import (load_blocks,
                                                 load_link,
                                                 load_page_publications,
                                                 load_page_title)
from cms.publications.models import Category
from cms.templates.models import PageTemplate, TemplateBlock
from cms.templates.blocks import *
from cms.templates.placeholders import *
from cms.templates.tests import TemplateUnitTest
from cms.templates.templatetags.unicms_templates import blocks_in_position

from . models import (Page, PageBlock, PageCarousel, PageContact,
                      PageHeading, PageHeadingLocalization, PageLink,
                      PageLocalization, PageMedia, PageMediaCollection,
                      PageMenu, PagePublication, PageRelated)
from . utils import copy_page_as_draft


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PageUnitTest(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST='example.org')


    @classmethod
    def create_category(cls, **kwargs):
        if not kwargs:
            kwargs =  {
                'name': 'main',
                'description': 'description',
                'image': f'{settings.MEDIA_ROOT}/images/categories/eventi.jpg'
            }
        obj = Category.objects.create(**kwargs)
        return obj


    @classmethod
    def create_page(cls, **kwargs):
        # templates
        page_template_block = TemplateUnitTest.create_page_block_template()
        page_template = page_template_block.template

        if kwargs.get('webpath'):
            webpath = kwargs.get('webpath')
        elif kwargs.get('webpath_path'):
            webpath = ContextUnitTest.create_webpath(path=kwargs.pop('webpath_path'))
        else:
            webpath = ContextUnitTest.create_webpath(path=datetime.datetime.now().strftime("%f"))

        data =  {'is_active': 1,
                 'draft_of': None,
                 'name': "Portale dell'Università della Calabria",
                 'title': 'titolo pagina',
                 'webpath': kwargs.get('webpath', None) or webpath,
                 'base_template': page_template,
                 'description': '',
                 'date_start': timezone.localtime(),
                 'date_end': None,
                 'state': 'published',
                 'type': 'home'}
        for k,v in kwargs.items():
            if k == 'webpath': continue
            data[k] = v

        obj = Page.objects.create(**data)

        # page related
        page_rel = PageRelated.objects.create(page=obj,
                                              related_page=obj,
                                              is_active=1)
        page_rel.__str__()

        # page menu
        menu = MenuUnitTest.create_menu()
        pm = PageMenu.objects.create(page = obj,
                                     menu=menu,
                                     is_active=1)
        pm.__str__()

        # page carousel
        carousel_item = CarouselUnitTest.create_carousel_item()
        carousel = carousel_item.carousel
        pc = PageCarousel.objects.create(page = obj,
                                         carousel=carousel,
                                         section='banner',
                                         is_active=1)
        pc.__str__()

        # page contact
        contact = ContactUnitTest.create_contact()
        pco = PageContact.objects.create(page = obj,
                                        contact=contact,
                                        section='1-right-b',
                                        is_active=1)
        pco.__str__()

        # page heading
        phead = PageHeading.objects.create(page = obj,
                                        title= 'page heading',
                                        description='description',
                                        is_active=1)
        pheadloc = PageHeadingLocalization.objects.create(heading = phead,
                                                          language='en',
                                                          title= 'page heading en',
                                                          description='description en',
                                                          is_active=1)
        phead.translate_as(lang='en')
        phead.__str__()

        # page media collection
        media_collection = MediaUnitTest.create_media_collection()
        phead = PageMediaCollection.objects.create(page = obj,
                                                   collection=media_collection,
                                                   is_active=1)
        phead.__str__()

        # page link
        pl = PageLink.objects.create(page = obj,
                                     name= 'page link',
                                     url='https://example.org')
        pl.__str__()

        # Page localization
        ploc = PageLocalization.objects.create(page=obj,
                                               language='en',
                                               title='page eng',
                                               is_active=1)
        ploc.__str__()

        # page block
        pb = PageBlock.objects.create(page=obj,
                                      block = page_template_block.block,
                                      is_active=1)
        pb.__str__()

        return obj


    @classmethod
    def create_page_menu(cls, **kwargs):
        menu = cls.create_menu()
        data = {'menu': menu,
                # 'parent_id': None,
                'name': 'Didattica',
                'url': 'http://example.org',
                # 'publication_id': None,
                # 'webpath_id': None,
                'is_active': True}
        for k,v in kwargs.items():
            data[k] = v
        obj = PageMenu.objects.create(**data)
        obj.category.add(cls.create_category())
        return obj


    @classmethod
    def test_category(cls):
        obj = cls.create_category()
        obj.__str__()
        obj.image_as_html()


    @classmethod
    def test_page(cls):
        obj = cls.create_page()
        obj.__str__()

        obj.get_publications()
        # test cached _pubs
        assert hasattr(obj, '_pubs')
        obj.get_publications()

        obj.get_blocks()
        obj.get_blocks(section='1')
        obj.get_blocks_placeholders()

        obj.get_carousels()
        # test cached carousels
        assert obj._carousels
        obj.get_carousels()

        obj.get_menus()
        # test cached menus
        assert obj._menus
        obj.get_menus()

        obj.get_links()
        # test cached links
        assert obj._links
        obj.get_links()

        obj.get_medias()
        # test cache medias
        # assert obj._medias -> test add some medias ...
        obj.get_medias()

        obj.translate_as(lang='en')

        # copy as draft
        copy_page_as_draft(obj)

        obj.delete()

    @classmethod
    def test_page_expired(cls):
        obj = cls.create_page(date_end=timezone.localtime())
        obj.is_publicable


    @classmethod
    def test_page_load_carousel(cls):
        obj = cls.create_page(date_end=timezone.localtime())
        req = RequestFactory().get('/')
        template_context = dict(request=req,
                                webpath=obj.webpath,
                                page=obj)

        data = dict(section='banner',
                    template='italia_carousel_hero_slider.html',
                    context=template_context)

        lm = load_carousel(**data)
        assert 'italia_carousel' in lm

        data['carousel_id'] = obj.get_carousels()[0].carousel.pk
        lm = load_carousel(**data)
        assert 'italia_carousel' in lm

        data['carousel_id'] = 101
        lm = load_carousel(**data)
        assert 'italia_carousel' not in lm


    @classmethod
    def test_page_load_contact(cls):
        obj = cls.create_page(date_end=timezone.localtime())
        req = RequestFactory().get('/')
        template_context = dict(request=req,
                                webpath=obj.webpath,
                                page=obj)

        data = dict(context=template_context,
                    section='1-right-b',
                    template='that.html')

        lm = load_contact(**data)
        assert lm

        contact = ContactUnitTest.create_contact()
        data = dict(context=template_context,
                    section='1-right-b',
                    template='that.html',
                    contact_id=contact.pk)

        lm2 = load_contact(**data)
        assert lm2


    # templatetag
    @classmethod
    def test_load_page_title(cls):
        req = RequestFactory().get('/')
        page = cls.create_page()
        template_context = dict(request=req,
                                page=page, webpath=page.webpath)

        data = dict(context=template_context)

        lm = load_page_title(**data)
        assert lm


    # templatetag
    @classmethod
    def test_load_link(cls):
        req = RequestFactory().get('/')
        page = cls.create_page()
        template_context = dict(request=req,
                                page=page, webpath=page.webpath)

        data = dict(context=template_context,
                    template='that.html', url='http://example.org')

        lm = load_link(**data)
        assert lm


    # templatetag
    def test_blocks_in_position(self):
        req = RequestFactory().get('/')
        page = self.create_page()

        # add a block in a sub section
        block_data = {'name': 'Test block',
                      'content': 'Hello world'}
        block_section = '1-top-a'
        tb = TemplateUnitTest.create_block_template(**block_data)

        # test page relateds cache cleanup
        for i in '_blocks_', '_pubs', '_carousels', '_medias', '_links':
            setattr(page, i, ['asdasd'])
        page.clean_related_caches()

        PageBlock.objects.create(page=page, block=tb,
                                 is_active=1, section=block_section)

        template_context = dict(request=req,
                                page=page, webpath=page.webpath)
        data = dict(context=template_context, section=block_section)
        lm = blocks_in_position(**data)
        self.assertTrue(lm)


    # templatetag
    @classmethod
    def test_load_menu(cls):
        req = RequestFactory().get('/')
        page = cls.create_page()
        template_context = dict(request=req,
                                page=page, webpath=page.webpath)

        data = dict(section='main-menu',
                    template='italia_main_menu.html',
                    context=template_context)

        lm = load_menu(**data)
        assert lm == '' # it's without page menu!

        # create a page menu with a real section
        menu = MenuUnitTest.create_menu()
        page_menu = PageMenu.objects.create(page=page,
                                            menu = menu,
                                            is_active=1,
                                            section='main-menu')
        lm = load_menu(**data)
        assert lm

        # with menu-id
        data['menu_id'] = menu.pk
        lm = load_menu(**data)
        assert lm

        # not existent menu-id
        data['menu_id'] = 100
        lm = load_menu(**data)
        assert lm == ''


    def test_home_page(self):
        obj = self.create_page(date_end=timezone.localtime(),
                               webpath_path='/')
        # ~ url = reverse('unicms:cms_dispatch')
        url = f'/{settings.CMS_PATH_PREFIX}'
        res = self.client.get(url)
        assert res.status_code == 200
        # testing cache
        res = self.client.get(url)
        assert res.status_code == 200


    def test_show_template_blocks_sections(self):
        self.create_page(webpath_path='/')
        user = ContextUnitTest.create_user(is_staff=1)
        self.client.force_login(user)
        # ~ url = reverse('unicms:cms_dispatch')
        url = f'/{settings.CMS_PATH_PREFIX}'
        res = self.client.get(f'{url}?show_template_blocks_sections')
        assert res.status_code == 200
        assert 'block' in res.content.decode()


    def show_cms_draft_mode(self):
        self.create_page()
        user = ContextUnitTest.create_user(is_staff=1)
        self.client.force_login(user)
        # ~ url = reverse('unicms:cms_dispatch')
        url = f'/{settings.CMS_PATH_PREFIX}'
        res = self.client.get(f'{url}?show_cms_draft_mode')
        assert res.status_code == 200

    # placeholders
    @classmethod
    def test_load_carousel_placeholder(cls):
        page = cls.create_page()
        webpath = page.webpath
        req = RequestFactory().get('/')

        block = CarouselPlaceholderBlock(
            request = req,
            webpath = webpath,
            page = page,
            content = '{"template" :"italia_hero_slider.html"}'
        )

        template_block = TemplateBlock.objects.create(
            name = 'carousel test',
            type = 'cms.templates.blocks.CarouselPlaceholderBlock',
            is_active = True
        )
        page_block = PageBlock.objects.create(page=page,
                                              block = template_block,
                                              is_active=1)
        lm = block.render()
        assert lm

    # placeholders
    @classmethod
    def test_load_contact_placeholder(cls):
        page = cls.create_page()
        webpath = page.webpath
        req = RequestFactory().get('/')

        block = ContactPlaceholderBlock(
            request = req,
            webpath = webpath,
            page = page,
            content = '{"template" :"that_template.html"}'
        )

        template_block = TemplateBlock.objects.create(
            name = 'contact test',
            type = 'cms.templates.blocks.ContactPlaceholderBlock',
            is_active = True
        )
        page_block = PageBlock.objects.create(page=page,
                                              block = template_block,
                                              is_active=1)
        lm = block.render()
        assert lm

    # placeholders
    @classmethod
    def test_load_link_placeholder(cls):
        page = cls.create_page()
        webpath = page.webpath
        req = RequestFactory().get('/')

        block = LinkPlaceholderBlock(
            request = req,
            webpath = webpath,
            page = page,
            content = '{"template": "italia_link.html"}'
        )

        template_block = TemplateBlock.objects.create(
            name = 'link test',
            type = 'cms.templates.blocks.LinkPlaceholderBlock',
            is_active = True
        )
        page_block = PageBlock.objects.create(page=page,
                                              block = template_block,
                                              is_active=1)
        lm = block.render()
        assert lm


    # placeholders
    @classmethod
    def test_load_media_placeholder(cls):
        page = cls.create_page()
        webpath = page.webpath
        req = RequestFactory().get('/')

        media = MediaUnitTest.create_media()
        page_media = PageMedia.objects.create(page=page, is_active=1,
                                              media=media)
        page_media.__str__()

        block = MediaPlaceholderBlock(
            request = req,
            webpath = webpath,
            page = page,
            content = '{"template": "italia_image.html"}'
        )

        template_block = TemplateBlock.objects.create(
            name = 'media test',
            type = 'cms.templates.blocks.MediaPlaceholderBlock',
            is_active = True
        )
        page_block = PageBlock.objects.create(page=page,
                                              block = template_block,
                                              is_active=1)
        lm = block.render()
        assert lm


    # placeholders
    @classmethod
    def test_load_menu_placeholder(cls):
        page = cls.create_page()
        webpath = page.webpath
        req = RequestFactory().get('/')

        menu = MenuUnitTest.create_menu_item().menu
        page_menu = PageMenu.objects.create(page=page, is_active=1,
                                            menu=menu)

        block = MenuPlaceholderBlock(
            request = req,
            webpath = webpath,
            page = page,
            content = '{"template": "italia_image.html"}'
        )

        template_block = TemplateBlock.objects.create(
            name = 'media test',
            type = 'cms.templates.blocks.MenuPlaceholderBlock',
            is_active = True
        )
        page_block = PageBlock.objects.create(page=page,
                                              block = template_block,
                                              is_active=1)
        lm = block.render().replace('\n', '')
        assert lm


    def test_page_preview(self):
        req = Client()
        page = self.create_page()
        user = ContextUnitTest.create_user(is_staff=1)
        url = reverse('unicms:page-preview',
                      kwargs={'page_id': page.pk})
        req.force_login(user)
        req.get(url)

        user.is_superuser = True
        user.save()
        req.get(url)


    # templatetag
    @classmethod
    def test_load_page_publications(cls):
        req = RequestFactory().get('/')
        page = cls.create_page()
        template_context = dict(request=req,
                                page=page, webpath=page.webpath)
        data = dict(context=template_context,
                    template='that.html')
        lpp = load_page_publications(**data)
        assert lpp

    # placeholders
    @classmethod
    def test_load_heading_placeholder(cls):
        page = cls.create_page()
        webpath = page.webpath
        req = RequestFactory().get('/')

        block = HeadingPlaceholderBlock(
            request = req,
            webpath = webpath,
            page = page,
            content = '{"template": "italia_heading.html"}'
        )

        template_block = TemplateBlock.objects.create(
            name = 'heading test',
            type = 'cms.templates.blocks.HeadingPlaceholderBlock',
            is_active = True
        )
        page_block = PageBlock.objects.create(page=page,
                                              block = template_block,
                                              is_active=1)
        lm = block.render()
        assert lm


    # placeholders
    @classmethod
    def test_load_mediacollection_placeholder(cls):
        page = cls.create_page()
        webpath = page.webpath
        req = RequestFactory().get('/')

        block = MediaCollectionPlaceholderBlock(
            request = req,
            webpath = webpath,
            page = page,
            content = '{"template": "template.html"}'
        )

        template_block = TemplateBlock.objects.create(
            name = 'heading test',
            type = 'cms.templates.blocks.MediaCollectionPlaceholderBlock',
            is_active = True
        )
        page_block = PageBlock.objects.create(page=page,
                                              block = template_block,
                                              is_active=1)
        lm = block.render()
        assert lm


    # templatetag
    @classmethod
    def test_load_item_childs(cls):
        req = RequestFactory().get('/')
        page = cls.create_page()
        template_context = dict(request=req,
                                page=page, webpath=page.webpath)

        parent = MenuUnitTest.create_menu_item()

        data = dict(item=parent,
                    context=template_context)

        childs = load_item_childs(**data)
        assert not childs

        child = MenuUnitTest.create_menu_item(menu_id=parent.menu.pk,
                                              parent_id=parent.pk)

        data = dict(item=parent,
                    context=template_context)

        childs = load_item_childs(**data)
        assert childs


    # templatetag
    @classmethod
    def test_load_item_inherited_content(cls):
        req = RequestFactory().get('/')
        page = cls.create_page()
        template_context = dict(request=req,
                                page=page, webpath=page.webpath)

        menu_item = MenuUnitTest.create_menu_item()

        data = dict(item=menu_item,
                    context=template_context)

        put = getattr(importlib.import_module('cms.publications.tests'), 'PublicationUnitTest')
        pub = put.create_pub()
        menu_item.inherited_content = pub
        menu_item.save()

        ic = load_item_inherited_content(**data)
        assert ic


    # templatetag
    @classmethod
    def test_load_item_publication(cls):
        req = RequestFactory().get('/')
        page = cls.create_page()
        template_context = dict(request=req,
                                page=page, webpath=page.webpath)

        menu_item = MenuUnitTest.create_menu_item()

        data = dict(item=menu_item,
                    context=template_context)

        put = getattr(importlib.import_module('cms.publications.tests'), 'PublicationUnitTest')
        pub = put.create_pub()
        menu_item.publication = pub
        menu_item.save()

        ic = load_item_publication(**data)
        assert ic


    # ~ def test_unicms_sitemap(self):
        # ~ obj = self.create_page(webpath_path='/')
        # ~ url = reverse('unicms_sitemap')
        # ~ res = self.client.get(url)
        # ~ assert res.status_code == 200


    def test_unicms_robots(self):
        obj = self.create_page(webpath_path='/')
        url = reverse('unicms_robots')
        res = self.client.get(url)
        assert res.status_code == 200


    # templatetag
    # @classmethod
    # def test_load_current_item_from_menu(cls):
        # req = RequestFactory().get('/portale/my/test')
        # page = cls.create_page()

        # webpath = ContextUnitTest.create_webpath(path='my/test')

        # parent = MenuUnitTest.create_menu_item()
        # child = MenuUnitTest.create_menu_item(menu=parent.menu,
                                              # parent=parent,
                                              # url='',
                                              # webpath=webpath)
        # template_context = dict(request=req,
                                # page=page,
                                # webpath=page.webpath,
                                # items=[parent])
        # data = dict(context=template_context)

        # ci = load_current_item_from_menu(**data)
        # assert ci


    # templatetag
    # @classmethod
    # def test_load_other_items_from_menu(cls):
        # req = RequestFactory().get('/portale/my/test')
        # page = cls.create_page()

        # webpath = ContextUnitTest.create_webpath(path='my/test')

        # parent = MenuUnitTest.create_menu_item()
        # child = MenuUnitTest.create_menu_item(menu=parent.menu,
                                              # parent=parent,
                                              # url='',
                                              # webpath=webpath)
        # child = MenuUnitTest.create_menu_item(menu=parent.menu,
                                              # parent=parent)
        # template_context = dict(request=req,
                                # page=page,
                                # webpath=page.webpath,
                                # items=[parent])
        # data = dict(context=template_context)

        # oi = load_other_items_from_menu(**data)
        # assert oi


class PageModelsUnitTest(TestCase):

    def test_is_publicable_draft(self):
        page = PageUnitTest.create_page(state='draft')
        assert page.is_active
        assert not page.is_publicable
        page.state = 'published'
        assert page.is_publicable

    def test_get_blocks_excluded_template_block(self):
        page = PageUnitTest.create_page()
        tpl_block = page.base_template.pagetemplateblock_set.first()
        assert tpl_block.block in page.get_blocks()
        # an inactive page block with same block/section/order
        # hides the template block
        page_block = PageBlock.objects.get(page=page)
        page_block.section = tpl_block.section
        page_block.order = tpl_block.order
        page_block.is_active = False
        page_block.save()
        page = Page.objects.get(pk=page.pk)
        assert page.get_blocks() == []

    def test_cached_related_items(self):
        page = PageUnitTest.create_page()
        # local import: cms.publications.tests imports this module
        from cms.publications.tests import PublicationUnitTest
        pub = PublicationUnitTest.create_pub(count=1)
        PagePublication.objects.create(page=page, publication=pub,
                                       is_active=True)
        PageMedia.objects.create(page=page,
                                 media=MediaUnitTest.create_media(),
                                 is_active=True)
        for getter, attr in (('get_publications', '_pubs'),
                             ('get_contacts', '_contacts'),
                             ('get_medias', '_medias'),
                             ('get_media_collections', '_media_collections'),
                             ('get_headings', '_headings')):
            first = getattr(page, getter)()
            assert first
            # second call returns the cached queryset
            assert getattr(page, getter)() is first
            assert getattr(page, attr) is first

    def test_is_lockable_by(self):
        page = PageUnitTest.create_page()
        user = ContextUnitTest.create_user(username='nobody', is_staff=True)
        superuser = ContextUnitTest.create_user(username='super',
                                                is_staff=True,
                                                is_superuser=True)
        page_block = PageBlock.objects.get(page=page)
        localization = PageLocalization.objects.get(page=page)
        heading_loc = PageHeadingLocalization.objects.get(heading__page=page)
        for obj in (page_block, localization, heading_loc):
            assert obj.is_lockable_by(superuser) is True
            assert obj.is_lockable_by(user) is False


class PageTemplateTagsUnitTest(TestCase):

    def test_load_blocks_render_error(self):
        page = PageUnitTest.create_page()
        block = TemplateUnitTest.create_block_template(
            content='{% load not_existent_templatetags %}'
        )
        block.section = 'banner'
        req = RequestFactory().get('/')
        req.user = ContextUnitTest.create_user()
        req.session = {}
        context = dict(request=req, page=page, webpath=page.webpath,
                       page_blocks=[block])
        # the faulty block is logged and skipped
        with self.assertLogs('cms.pages.templatetags.unicms_pages',
                             level='ERROR'):
            result = load_blocks(context, section='banner')
        assert result == ''

    def test_load_page_publications_translated(self):
        page = PageUnitTest.create_page()
        # local import: cms.publications.tests imports this module
        from cms.publications.tests import PublicationUnitTest
        pub = PublicationUnitTest.create_pub(count=1)
        PagePublication.objects.create(page=page, publication=pub,
                                       is_active=True)
        req = RequestFactory().get('/')
        req.LANGUAGE_CODE = 'en'
        context = dict(request=req, page=page, webpath=page.webpath)
        result = load_page_publications(context=context,
                                        template='that.html')
        assert result
        assert page.get_publications()[0].publication.title == 'pub eng'


class PageAdminActionsUnitTest(TestCase):

    def test_update_template(self):
        page = PageUnitTest.create_page()
        new_template = TemplateUnitTest.create_page_template(name='new tpl')
        user = ContextUnitTest.create_user(username='admin',
                                           is_staff=True,
                                           is_superuser=True)
        req = Client()
        req.force_login(user)
        url = reverse('admin:cmspages_page_changelist')
        data = {'action': 'update_template',
                '_selected_action': [page.pk]}
        # first step: template choice form
        res = req.post(url, data)
        assert res.status_code == 200
        assert 'form' in res.context
        assert page in res.context['pages']
        # invalid template: form is shown again
        res = req.post(url, dict(data, update_template=1, template=999999))
        assert res.status_code == 200
        page.refresh_from_db()
        assert page.base_template != new_template
        # valid template
        res = req.post(url, dict(data, update_template=1,
                                 template=new_template.pk))
        assert res.status_code == 302
        page.refresh_from_db()
        assert page.base_template == new_template


class PageSerializersUnitTest(TestCase):

    def test_foreign_keys_without_request(self):
        from . serializers import (PageBlockSerializer,
                                   PageHeadingLocalizationSerializer,
                                   PageSerializer)
        # without a request in context there is no queryset to choose from
        assert PageBlockSerializer().fields['page'].get_queryset() is None
        assert PageSerializer().fields['webpath'].get_queryset() is None
        heading_field = PageHeadingLocalizationSerializer().fields['heading']
        assert heading_field.get_queryset() is None

    def test_empty_date_end(self):
        from . serializers import PageSerializer
        page = PageUnitTest.create_page(date_end=timezone.localtime())
        serializer = PageSerializer(instance=page,
                                    data={'date_end': ''},
                                    partial=True)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['date_end'] is None
