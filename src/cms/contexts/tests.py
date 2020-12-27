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
        
    def test_parented_webpath(self):
        webpath = self.create_webpath()
        kwargs =  {'name': "Example WebPath child1",
                   'parent': webpath,
                   'path': 'child1/',
                   'is_active': True}
        webpath2 = WebPath.objects.create(**kwargs)
        assert webpath2.get_full_path() == sanitize_path(f'/{CMS_PATH_PREFIX}/{webpath.path}/{webpath2.path}')
        
    def test_aliased_webpath(self):
        webpath = self.create_webpath()
        kwargs =  {'name': "Example WebPath alias",
                   'alias': webpath,
                   'path': 'alias/',
                   'is_active': True}
        webpath2 = WebPath.objects.create(**kwargs)
        assert webpath2.get_full_path() == sanitize_path(f'/{CMS_PATH_PREFIX}/{webpath.path}')
