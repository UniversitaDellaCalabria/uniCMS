import logging

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from . models import *
from . settings import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ContextsTest(TestCase):
    def setUp(self):
        pass
        
    def create_website(self, **kwargs):
        kwargs = kwargs or dict(name='example.org',
                                domain='example.org',
                                is_active=True)
        website = WebSite.objects.create(**kwargs)
        return website
    
    def create_webpath(self, **kwargs):
        if not kwargs:
            website = self.create_website()
            kwargs =  {'site': website,
                       'name': "Example WebPath",
                       'parent': None,
                       'alias': None,
                       'alias_url': None,
                       'path': '/',
                       'is_active': True}

        webpath = WebPath.objects.create(**kwargs)
        return webpath
    
    def test_webpath(self):
        webpath = self.create_webpath()
        webpath.__str__()
        assert webpath.split() == ['/']
        
        # test without alias
        assert not webpath.is_alias
        assert not webpath.redirect_url
        
        assert webpath.get_full_path() == sanitize_path(f'/{CMS_PATH_PREFIX}/{webpath.path}')
        
        
