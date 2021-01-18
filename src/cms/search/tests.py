import logging

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from cms.publications.tests import PublicationUnitTest
from cms.templates.tests import TemplateUnitTest



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TemplateUnitTest(TestCase):

    def setUp(self):
        pass

    def test_api_search(self):
        pub = PublicationUnitTest.enrich_pub()
        pub.related_contexts[0].webpath
        
        req = Client()
        url = reverse('unicms_search:api-search-engine')
        res = req.get(url, content_type='application/json')
        assert isinstance(res.json(), dict)

        # categories
        res = req.get(url+'?categories=ciao,mamma', content_type='application/json')
        assert isinstance(res.json(), dict)

        # tags
        res = req.get(url+'?tags=ciao,mamma', content_type='application/json')
        assert isinstance(res.json(), dict)
        
        # sites
        res = req.get(url+'?sites=unical.it,example.org', content_type='application/json')
        assert isinstance(res.json(), dict)
        
        # search
        res = req.get(url+'?search=lorem ipsum', content_type='application/json')
        assert isinstance(res.json(), dict)

        # year
        res = req.get(url+f'?year={timezone.now().year}', content_type='application/json')
        assert isinstance(res.json(), dict)
        
        # date_start
        res = req.get(url+f'?date_start={timezone.now().strftime("%Y-%m-%d")}', content_type='application/json')
        assert isinstance(res.json(), dict)
        
        # date_end
        res = req.get(url+f'?date_end={timezone.now().strftime("%Y-%m-%d")}', content_type='application/json')
        assert isinstance(res.json(), dict)

        # wrong page number
        res = req.get(url+f'?page_number=a', content_type='application/json')
        assert isinstance(res.json(), dict)

        # wrong page number #2
        res = req.get(url+f'?page_number=1024', content_type='application/json')
        assert isinstance(res.json(), dict)
