import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from cms.carousels.templatetags.unicms_carousels import load_carousel
from cms.carousels.tests import CarouselUnitTest
from cms.contexts.tests import ContextUnitTest
from cms.menus.tests import MenuUnitTest
from cms.templates.tests import TemplateUnitTest

from . models import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PageUnitTest(TestCase):

    def setUp(self):
        pass


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
        
        data =  {'is_active': 1,
                   'draft_of': None, 
                   'name': "Portale dell'Università della Calabria", 
                   'title': 'titolo pagina', 
                   'webpath': ContextUnitTest.create_webpath(), 
                   'base_template': page_template, 
                   'description': '', 
                   'date_start': timezone.localtime(), 
                   'date_end': None, 
                   'state': 'published', 
                   'type': 'home'}
        for k,v in kwargs.items():
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
        obj.get_publications()

        obj.get_blocks()
        obj.get_blocks(section='1')
        obj.get_blocks_placeholders()

        obj.get_carousels()
        # test cached carousels
        obj.get_carousels()
        
        obj.get_menus()
        # test cached menus
        obj.get_menus()
        
        obj.get_links()
        # test cached links
        obj.get_links()
        
        obj.translate_as(lang='en')
        
        obj.delete()
    
    @classmethod
    def test_page_expired(cls):
        obj = cls.create_page(date_end=timezone.localtime())
        obj.is_publicable
    
    
    @classmethod
    def test_page_load_carousel(cls):
        obj = cls.create_page(date_end=timezone.localtime())
        req = RequestFactory().get('/')
        template_context = dict(request=req, webpath=obj.webpath)
        lm = load_carousel(section='banner',  
                           template='italia_hero_slider.html',
                           context=template_context)
        assert 'italia_carousel' in lm
