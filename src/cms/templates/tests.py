import logging
import urllib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils import timezone

from . models import *
from . utils import get_unicms_templates


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TemplateUnitTest(TestCase):

    def setUp(self):
        pass


    def create_page_template(self, **kwargs):
        data = {'is_active': True, 
                'name': 'Bootstrap Italia', 
                'template_file': 'italia.html', 
                'image': 'media/images/categories/eventi.jpg', 
                'note': 'blah blah'}
        for k,v in kwargs.items():
            data[k] = v
        pt = PageTemplate.objects.create(**data)
        return pt


    def create_block_template(self, **kwargs):
        data = {'is_active': True, 
                'name': 'Carousel - Main Banner', 
                'description': '', 
                'type': 'cms.templates.blocks.HtmlBlock', 
                'content': '{% load unicms_carousels %}\r\n{% load_carousel section=\'banner\' template="italia_hero_slider.html" %}', 
                'image': ''}
        for k,v in kwargs.items():
            data[k] = v
        tb = TemplateBlock.objects.create(**data)
        return tb


    def create_page_block_template(self, page_data={}, block_data={}):
        if page_data:
            pt = self.create_page_template(**page_data)
        else:
            pt = self.create_page_template()

        if block_data:
            bt = self.create_block_template(**block_data)
        else:
            bt = self.create_block_template()
        return PageTemplateBlock(template=pt, block=bt, section='1')

        
    def test_template_page_block(self):
        ptb = self.create_page_block_template()
        
        ptb.template.__str__()
        ptb.block.__str__()
        ptb.__str__()
        
        ptb.template.image_as_html()
        ptb.block.image_as_html()
        
        ptb.type
        ptb.content
    
    def test_unicms_template(self):
        res = get_unicms_templates()
        assert isinstance(res, list) and len(res) > 1
