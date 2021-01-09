import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from cms.contexts.models import WebPath
from cms.contexts.tests import ContextUnitTest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class APIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_website_list(self):
        req = Client()
        user = ContextUnitTest.create_user(username='user-1')
        webpath = ContextUnitTest.create_webpath()
        # two editorialboard_user with different webpaths
        ContextUnitTest.create_editorialboard_user(user=user,
                                                   webpath=webpath,
                                                   permission=1,
                                                   is_active=True)
        ContextUnitTest.create_editorialboard_user(user=user,
                                                   webpath=None,
                                                   permission=8,
                                                   is_active=True)
        url = reverse('unicms_api:editorial-board-site-list')
        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

    def test_webpath_list(self):
        req = Client()
        ebu = ContextUnitTest.create_editorialboard_user()
        url = reverse('unicms_api:editorial-board-site-webpath-list',
                      kwargs={'site_id': ebu.webpath.site.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user = ebu.user
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

    def test_webpath_view(self):
        req = Client()
        ebu = ContextUnitTest.create_editorialboard_user()
        webpath = ebu.webpath
        url = reverse('unicms_api:editorial-board-site-webpath-view',
                      kwargs={'site_id': webpath.site.pk,
                              'webpath_id': webpath.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user = ebu.user
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

    def test_webpath_patch(self):
        req = Client()
        ebu_parent = ContextUnitTest.create_editorialboard_user()
        parent = ebu_parent.webpath
        parent_url = reverse('unicms_api:editorial-board-site-webpath-view',
                             kwargs={'site_id': parent.site.pk,
                                     'webpath_id': parent.pk})
        parent_json = {'name': 'edited name'}

        # accessible to staff users only
        res = req.patch(parent_url,
                        data=parent_json,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        user = ebu_parent.user
        user.is_staff = True
        user.save()
        req.force_login(user)

        # if not publisher permissions
        assert res.status_code == 403
        # if publisher permissions
        ebu_parent.permission = 7
        ebu_parent.save()
        res = req.patch(parent_url,
                        data=parent_json,
                        content_type='application/json',
                        follow=1)
        parent.refresh_from_db()
        assert parent.name == 'edited name'

        # edit child parent
        ebu_child = ContextUnitTest.create_editorialboard_user(user=user,
                                                               webpath=ContextUnitTest.create_webpath(),
                                                               permission=3,
                                                               is_active=True)
        child = ebu_child.webpath
        child_url = reverse('unicms_api:editorial-board-site-webpath-view',
                            kwargs={'site_id': child.site.pk,
                                    'webpath_id': child.pk})

        # wrong child permissions
        child_json = {}
        res = req.patch(child_url,
                        data=child_json,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403

        # fix child permissions
        ebu_child.permission = 7
        ebu_child.save()

        # wrong parent
        child_json = {'parent': 100023123123123}
        res = req.patch(child_url,
                        data=child_json,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 404

        # wrong permissions on parent
        ebu_parent.permission = 3
        ebu_parent.save()
        child_json = {'parent': parent.pk}
        res = req.patch(child_url,
                        data=child_json,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403

        # correct data and permissions on parent
        ebu_parent.permission = 7
        ebu_parent.save()

        # wrong alias
        child_json = {'alias': 12312321312}
        res = req.patch(child_url,
                        data=child_json,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 404

        # correct alias
        child_json = {'alias': parent.pk}
        res = req.patch(child_url,
                        data=child_json,
                        content_type='application/json',
                        follow=1)
        child.refresh_from_db()
        assert child.alias == parent

        child_json = {'alias': None}
        res = req.patch(child_url,
                        data=child_json,
                        content_type='application/json',
                        follow=1)
        child.refresh_from_db()
        assert isinstance(res.json(), dict)

        child_json = {'alias_url': 'https://www.unical.it'}
        res = req.patch(child_url,
                        data=child_json,
                        content_type='application/json',
                        follow=1)
        child.refresh_from_db()
        assert child.alias_url == 'https://www.unical.it'

        child_json = {'is_active': False}
        res = req.patch(child_url,
                        data=child_json,
                        content_type='application/json',
                        follow=1)
        child.refresh_from_db()
        assert child.is_active == False

    def test_webpath_delete(self):
        req = Client()
        ebu = ContextUnitTest.create_editorialboard_user()
        webpath = ebu.webpath
        url = reverse('unicms_api:editorial-board-site-webpath-view',
                      kwargs={'site_id': webpath.site.pk,
                              'webpath_id': webpath.pk})

        # accessible to staff users only
        res = req.delete(url)
        assert res.status_code == 403
        user = ebu.user
        user.is_staff = True
        user.save()
        req.force_login(user)

        # wrong permissions
        res = req.delete(url)
        assert res.status_code == 403

        # publisher permission on webpath
        ebu.permission = 7
        ebu.save()
        res = req.delete(url)
        try:
            webpath.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

    def test_webpath_new(self):
        req = Client()
        ebu_parent = ContextUnitTest.create_editorialboard_user()
        parent = ebu_parent.webpath

        # data with wrong parent
        data = {'parent': 123123123213,
                'name': 'test webpath',
                'path': 'test'}
        url = reverse('unicms_api:editorial-board-site-webpath-new',
                      kwargs={'site_id': parent.site.pk})

        # accessible to staff users only
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert res.status_code == 403
        user = ebu_parent.user
        user.is_staff = True
        user.save()
        req.force_login(user)

        # wrong parent
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert res.status_code == 404

        # correct parent but invalid permissions
        data['parent'] = parent.pk
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert res.status_code == 403

        # update permissions on parent webpath
        ebu_parent.permission = 7
        ebu_parent.save()

        # invalid alias
        data['alias'] = 1231231
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert res.status_code == 404

        # valid alias
        data['alias'] = parent.pk
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert WebPath.objects.filter(name='test webpath').first()
