import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils import timezone

from . models import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MediaTest(TestCase):

    def setUp(cls):
        pass

    @classmethod
    def create_media(cls, **kwargs):
        data = {'title': 'media1', 
                'file': f'{settings.MEDIA_ROOT}/images/categories/eventi.jpg',
                'description': 'blah blah',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = Media.objects.create(**data)
        return obj
