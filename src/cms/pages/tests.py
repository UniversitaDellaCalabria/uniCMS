import importlib
import logging
import datetime

from django.conf import settings
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from cms.carousels.templatetags.unicms_carousels import load_carousel
from cms.carousels.tests import CarouselUnitTest
from cms.contexts.tests import ContextUnitTest
from cms.medias.tests import MediaUnitTest
from cms.menus.tests import MenuUnitTest
from cms.menus.templatetags.unicms_menus import *
from cms.pages.templatetags.unicms_pages import (load_link,
                                                 load_page_publications,
                                                 load_page_title)
from cms.publications.models import Category
from cms.templates.models import TemplateBlock
from cms.templates.blocks import *
from cms.templates.placeholders import *
from cms.templates.tests import TemplateUnitTest
from cms.templates.templatetags.unicms_templates import blocks_in_position

from . models import (Page, PageBlock, PageCarousel,
                      PageHeading, PageHeadingLocalization, PageLink,
                      PageLocalization, PageMedia, PageMediaCollection,
                      PageMenu, PageRelated)
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

        data['carousel_id'] = obj.get_carousels()[0].pk
        lm = load_carousel(**data)
        assert 'italia_carousel' in lm

        data['carousel_id'] = 101
        lm = load_carousel(**data)
        assert 'italia_carousel' not in lm


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
        url = reverse('unicms:cms_dispatch')
        res = self.client.get(url)
        assert res.status_code == 200
        # testing cache
        res = self.client.get(url)
        assert res.status_code == 200


    def test_show_template_blocks_sections(self):
        self.create_page(webpath_path='/')
        user = ContextUnitTest.create_user(is_staff=1)
        self.client.force_login(user)
        url = reverse('unicms:cms_dispatch')
        res = self.client.get(f'{url}?show_template_blocks_sections')
        assert res.status_code == 200
        assert 'block' in res.content.decode()


    def show_cms_draft_mode(self):
        self.create_page()
        user = ContextUnitTest.create_user(is_staff=1)
        self.client.force_login(user)
        url = reverse('unicms:cms_dispatch')
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


    # templatetag
    @classmethod
    def test_load_current_item_from_menu(cls):
        req = RequestFactory().get('/portale/my/test')
        page = cls.create_page()

        webpath = ContextUnitTest.create_webpath(path='my/test')

        parent = MenuUnitTest.create_menu_item()
        child = MenuUnitTest.create_menu_item(menu=parent.menu,
                                              parent=parent,
                                              url=None,
                                              webpath=webpath)
        template_context = dict(request=req,
                                page=page,
                                webpath=page.webpath,
                                items=[parent])
        data = dict(context=template_context)

        ci = load_current_item_from_menu(**data)
        assert ci


    # templatetag
    @classmethod
    def test_load_other_items_from_menu(cls):
        req = RequestFactory().get('/portale/my/test')
        page = cls.create_page()

        webpath = ContextUnitTest.create_webpath(path='my/test')

        parent = MenuUnitTest.create_menu_item()
        child = MenuUnitTest.create_menu_item(menu=parent.menu,
                                              parent=parent,
                                              url=None,
                                              webpath=webpath)
        child = MenuUnitTest.create_menu_item(menu=parent.menu,
                                              parent=parent)
        template_context = dict(request=req,
                                page=page,
                                webpath=page.webpath,
                                items=[parent])
        data = dict(context=template_context)

        oi = load_other_items_from_menu(**data)
        assert oi
