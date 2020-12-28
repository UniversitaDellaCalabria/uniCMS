import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from . templatetags.unicms_contexts import *
from . models import *
from . settings import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ContextsTest(TestCase):

    def setUp(self):
        pass


    def create_user(self, **kwargs):
        if not kwargs:
            kwargs =  {'username': 'foo',
                       'first_name': 'foo',
                       'last_name': 'bar',
                       'email': 'that@mail.org'}
        user = get_user_model().objects.create(**kwargs)
        return user


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

    def create_editorialboard_user(self, **kwargs):
        if not kwargs:
            webpath = self.create_webpath()
            kwargs =  {'user': self.create_user(),
                       'permission': '1',
                       'webpath': self.create_webpath(),
                       'is_active': True}

        ebe = EditorialBoardEditors.objects.create(**kwargs)
        return ebe


    def test_webpath(self):
        webpath = self.create_webpath()
        webpath.__str__()
        assert webpath.split() == ['/']
        
        # test without alias
        assert not webpath.is_alias
        assert not webpath.redirect_url
        
        assert webpath.get_full_path() == \
            sanitize_path(f'/{CMS_PATH_PREFIX}/{webpath.path}')


    def test_parented_webpath(self):
        webpath = self.create_webpath()
        kwargs =  {'name': "Example WebPath child1",
                   'parent': webpath,
                   'path': 'child1/',
                   'is_active': True}
        webpath2 = WebPath.objects.create(**kwargs)
        assert webpath2.get_full_path() == \
            sanitize_path(f'/{CMS_PATH_PREFIX}/{webpath.path}/{webpath2.path}')
        

    def test_aliased_webpath(self):
        webpath = self.create_webpath()
        kwargs =  {'name': "Example WebPath alias",
                   'alias': webpath,
                   'path': 'alias/',
                   'is_active': True}
        webpath2 = WebPath.objects.create(**kwargs)
        assert webpath2.get_full_path() == \
            sanitize_path(f'/{CMS_PATH_PREFIX}/{webpath.path}')
        
        assert webpath2.redirect_url == webpath.get_full_path()
        
        # change to a third party url
        _url = 'http://example.org'
        webpath2.alias_url = _url
        webpath2.alias = None
        assert webpath2.redirect_url == _url == webpath2.get_full_path()


    def test_editorialboard_user(self):
        ebe = self.create_editorialboard_user()
        ebe.__str__()

    # start Template tags tests
    def tests_templatetags_breadcrumbs(self):
        webpath = self.create_webpath()
        kwargs =  {'name': "Example WebPath child1",
                   'parent': webpath,
                   'path': 'child1/',
                   'is_active': True}
        webpath2 = WebPath.objects.create(**kwargs)
        breadc = breadcrumbs(webpath=webpath2)
        assert webpath.get_full_path() in breadc
        assert webpath2.get_full_path() in breadc

    # Template tag
    def tests_templatetags_cms_sites(self):
        self.create_website()
        assert len(cms_sites()) == 1
    
    # Template tag
    def tests_templatetags_call(self):
        webpath = self.create_webpath()
        assert call(webpath, 'split')

    # Template tag
    def tests_templatetags_language_menu(self):
        req = RequestFactory().get('/')
        template_context = dict(request=req)
        lm = language_menu(context=template_context)
        assert lm and isinstance(lm, dict) 
    # end Template tags tests
