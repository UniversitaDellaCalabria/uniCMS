import datetime
import logging

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase


from . exceptions import ReservedWordException
from . models import *
from . settings import *
from . templatetags.unicms_contexts import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ContextUnitTest(TestCase):

    def setUp(self):
        pass


    @classmethod
    def create_user(cls, **kwargs):
        data =  {'username': 'foo',
                 'first_name': 'foo',
                 'last_name': 'bar',
                 'email': 'that@mail.org'}
        for k,v in kwargs.items():
            data[k] = v
        user = get_user_model().objects.create(**data)
        return user


    @classmethod
    def create_website(cls, **kwargs):
        kwargs = kwargs or dict(name='example.org',
                                domain='example.org',
                                is_active=True)
        website = WebSite.objects.filter(**kwargs).first() or \
                  WebSite.objects.create(**kwargs)
        return website


    @classmethod
    def create_webpath(cls, **kwargs):
        data = {'site': cls.create_website(),
                'name': "Example WebPath",
                'parent': None,
                'alias': None,
                'alias_url': None,
                'path': '/',
                'is_active': True}
        for k,v in kwargs.items():
            data[k] = v
        obj = WebPath.objects.create(**data)
        return obj


    @classmethod
    def create_editorialboard_user(cls, **kwargs):
        data = {'user': cls.create_user() if not kwargs.get('user') else kwargs['user'],
                'permission': 1,
                'webpath': kwargs.get('webpath') or cls.create_webpath(path=datetime.datetime.now().strftime("%f")),
                'is_active': True}
        for k,v in kwargs.items():
            if k == 'webpath': continue
            data[k] = v
        obj = EditorialBoardEditors.objects.create(**data)
        obj.serialize()
        return obj


    def test_webpath(self):
        webpath = self.create_webpath()
        webpath.__str__()
        assert webpath.split() == ['/']

        # test without alias
        assert not webpath.is_alias
        assert not webpath.redirect_url

        assert webpath.get_full_path() == \
            sanitize_path(f'/{CMS_PATH_PREFIX}/{webpath.path}')

        # test reserved words
        webpath.path = 'that/contents/news/view'
        try:
            webpath.save()
        except Exception as e:
            assert isinstance(e, ReservedWordException)

        # test split
        webpath.path = '/test/io'
        webpath.save()
        res = webpath.split()
        assert isinstance(res, list) and len(res) > 1

        webpath.delete()

    def test_parented_webpath(self):
        webpath = self.create_webpath()
        kwargs =  {'name': "Example WebPath child1",
                   'parent': webpath,
                   'path': 'child1/',
                   'is_active': True}
        webpath2 = WebPath.objects.create(**kwargs)
        assert webpath2.get_full_path() == \
            sanitize_path(f'/{CMS_PATH_PREFIX}/{webpath.path}/{webpath2.path}')

        # covers child updates
        webpath.save()

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

        perm_dict = dict(CMS_CONTEXT_PERMISSIONS)

        ebe_q = dict(webpath = ebe.webpath, user = ebe.user)

        for i in range(1,8):
            # test some permissions
            perm = EditorialBoardEditors.get_permission(**ebe_q)
            logger.debug(f'User {ebe.user} {perm_dict[perm]}')
            ebe.permission += 1
            ebe.save()

        # test parent permissions
        ebe_q['check_all'] = 1
        ebe.permission = 1
        ebe.webpath = None
        ebe.save()

        perm = EditorialBoardEditors.get_permission(**ebe_q)
        assert perm

        # test parent permissions
        parent = self.create_webpath(path="path-1")
        webpath = self.create_webpath(path="path-2", parent=parent)
        user = ebe.user
        ebe.delete()
        parent_ebe = self.create_editorialboard_user(user=user,
                                                     permission=2,
                                                     webpath=parent)
        EditorialBoardEditors.get_permission(user=user, webpath=webpath)

        # test no permission webpath
        webpath = self.create_webpath(path="path-3")
        EditorialBoardEditors.get_permission(user=user, webpath=webpath, check_all=False)


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
