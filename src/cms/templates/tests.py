import logging

from django.test import TestCase

from . models import PageTemplate, PageTemplateBlock, TemplateBlock
from . utils import get_unicms_templates


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TemplateUnitTest(TestCase):

    def setUp(self):
        pass

    @classmethod
    def create_page_template(cls, **kwargs):
        data = {'is_active': True, 
                'name': 'Bootstrap Italia', 
                'template_file': 'italia.html', 
                'image': 'media/images/categories/eventi.jpg', 
                'note': 'blah blah'}
        for k,v in kwargs.items():
            data[k] = v
        pt = PageTemplate.objects.create(**data)
        pt.__str__()
        return pt

    @classmethod
    def create_block_template(cls, **kwargs):
        data = {'is_active': True, 
                'name': 'Carousel - Main Banner', 
                'description': '', 
                'type': 'cms.templates.blocks.HtmlBlock', 
                'content': '{% load unicms_carousels %}\r\n{% load_carousel section=\'banner\' template="italia_hero_slider.html" %}', 
                'image': ''}
        for k,v in kwargs.items():
            data[k] = v
        tb = TemplateBlock.objects.create(**data)
        tb.__str__()
        return tb


    @classmethod
    def create_page_block_template(cls, page_data={}, block_data={}, **kwargs):
        if page_data:
            pt = cls.create_page_template(**page_data)
        else:
            pt = cls.create_page_template()

        if block_data:
            bt = cls.create_block_template(**block_data)
        else:
            bt = cls.create_block_template()
        data = kwargs.copy()
        data['template'] = pt
        data['block'] = bt
        data['section'] = 'banner'
        data['is_active'] = True
        for k,v in kwargs.items():
            data[k] = v
        return PageTemplateBlock.objects.create(**data)

        
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
