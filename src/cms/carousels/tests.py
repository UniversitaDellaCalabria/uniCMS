import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils import timezone

from cms.medias.tests import MediaTest

from . models import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CarouselTest(TestCase):

    def setUp(cls):
        pass

    @classmethod
    def create_carousel(cls, **kwargs):
        data = {'name': 'carousel1', 
                'description': 'blah blah',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = Carousel.objects.create(**data)
        return obj


    @classmethod
    def create_carousel_item(cls, carousel_data={}, **kwargs):
        if carousel_data:
            carousel = cls.create_carousel(**carousel_data)
        else:
            carousel = cls.create_carousel()
        data = {'carousel': carousel, 
                'heading': 'heading', 
                'pre_heading': 'pre heading', 
                'image': MediaTest.create_media(), 
                'description': 'blah blah',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = CarouselItem.objects.create(**data)
        return obj


    @classmethod
    def create_carousel_item_localization(cls, 
                                  carousel_data={},
                                  carousel_data_item={}, 
                                  **kwargs):
        carousel_item = cls.create_carousel_item(carousel_data=carousel_data,
                                                  **carousel_data_item)
        data = {'carousel_item': carousel_item, 
                'language': 'en', 
                'pre_heading': 'pre heading eng',
                'heading': 'heading en',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = CarouselItemLocalization.objects.create(**data)
        return obj    


    @classmethod
    def create_carousel_item_link(cls, 
                                  carousel_data={},
                                  carousel_data_item={}, 
                                  **kwargs):
        carousel_item = cls.create_carousel_item(carousel_data=carousel_data,
                                        **carousel_data_item)
        data = {'carousel_item': carousel_item, 
                'item': 'pre heading', 
                'url': '/that/url',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = CarouselItemLink.objects.create(**data)
        return obj    


    def test_carousel(cls):
        carousel_item_localization = cls.create_carousel_item_localization()
