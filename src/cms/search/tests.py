import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from cms.carousels.tests import CarouselUnitTest
from cms.contexts.tests import ContextUnitTest
from cms.medias.tests import MediaUnitTest
from cms.menus.tests import MenuUnitTest
from cms.pages.tests import PageUnitTest
from cms.publications.tests import PublicationUnitTest
from cms.templates.tests import TemplateUnitTest

from . models import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TemplateUnitTest(TestCase):

    def setUp(self):
        pass

    def test_api_search(self):
        pub = PublicationUnitTest.enrich_pub()
        webpath = pub.related_contexts[0].webpath
        
        req = Client()
        url = reverse('unicms_search:api-search-engine')
        res = req.get(url, content_type='application/json')
        assert isinstance(res.json(), dict)
