import logging

from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse


from cms.contexts.models import WebPath
from cms.contexts.tests import ContextUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class WebpathAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_list(self):
        req = Client()
        ebu = ContextUnitTest.create_editorialboard_user()
        url = reverse('unicms_api:editorial-board-site-webpaths',
                      kwargs={'site_id': ebu.webpath.site.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user = ebu.user
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url, {'is_active': True})
        assert isinstance(res.json(), dict)

    def test_get(self):
        req = Client()
        ebu = ContextUnitTest.create_editorialboard_user()
        webpath = ebu.webpath
        url = reverse('unicms_api:editorial-board-site-webpath',
                      kwargs={'site_id': webpath.site.pk,
                              'pk': webpath.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user = ebu.user
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

    def test_patch(self):
        req = Client()
        ebu_parent = ContextUnitTest.create_editorialboard_user()
        ebu = ContextUnitTest.create_editorialboard_user(user=ebu_parent.user)
        ebu.webpath.parent = ebu_parent.webpath
        ebu.webpath.save()

        url = reverse('unicms_api:editorial-board-site-webpath',
                      kwargs={'site_id': ebu.webpath.site.pk,
                              'pk': ebu.webpath.pk})

        data = {'site': 12321321}
        # accessible to staff users only
        res = req.patch(url,
                        data=data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        user = ebu.user
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.patch(url,
                        data=data,
                        content_type='application/json',
                        follow=1)
        # invalid site
        assert res.status_code == 403
        # invalid parent
        data = {'parent': 123123123}
        res = req.patch(url,
                        data=data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 404
        # valid data but...
        data = {'name': 'patched name',
                'is_active': 0}
        res = req.patch(url,
                        data=data,
                        content_type='application/json',
                        follow=1)
        # ...no publisher permissions on parent
        assert res.status_code == 403
        # if publisher permissions
        ebu_parent.permission = 7
        ebu_parent.save()
        res = req.patch(url,
                        data=data,
                        content_type='application/json',
                        follow=1)
        ebu.webpath.refresh_from_db()
        assert ebu.webpath.name == 'patched name'
        assert not ebu.webpath.is_active
        # valid parent
        data = {'parent': ebu_parent.webpath.pk}
        res = req.patch(url,
                        data=data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 200

    def test_put(self):
        req = Client()
        site = ContextUnitTest.create_website()
        root_webpath = ContextUnitTest.create_webpath(site=site)
        ebu_parent = ContextUnitTest.create_editorialboard_user()
        ebu_root = ContextUnitTest.create_editorialboard_user(user=ebu_parent.user,
                                                              webpath=root_webpath,
                                                              permission=7)
        parent = ebu_parent.webpath
        parent.site = site
        parent.parent = root_webpath
        parent.save()

        parent_url = reverse('unicms_api:editorial-board-site-webpath',
                             kwargs={'site_id': parent.site.pk,
                                     'pk': parent.pk})

        parent_json = {'site': site.pk,
                       'parent': root_webpath.pk,
                       'name': 'edited name',
                       'path': 'test',
                       'is_active': 1}

        # accessible to staff users only
        res = req.put(parent_url,
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
        res = req.put(parent_url,
                      data=parent_json,
                      content_type='application/json',
                      follow=1)
        parent.refresh_from_db()
        assert parent.name == 'edited name'

        # no site
        parent_json['site'] = None
        res = req.put(parent_url, data=parent_json,
                      content_type='application/json', follow=1)
        assert res.status_code == 404
        parent_json['site'] = site.pk

        # no parent
        parent_json['parent'] = None
        res = req.put(parent_url, data=parent_json,
                      content_type='application/json', follow=1)
        assert res.status_code == 404
        parent_json['parent'] = root_webpath.pk

        # edit child parent
        ebu_child = ContextUnitTest.create_editorialboard_user(user=user,
                                                               webpath=ContextUnitTest.create_webpath(),
                                                               permission=3,
                                                               is_active=True)
        child = ebu_child.webpath
        child_url = reverse('unicms_api:editorial-board-site-webpath',
                            kwargs={'site_id': site.pk,
                                    'pk': child.pk})

        # wrong child permissions
        child_json = {}
        res = req.put(child_url,
                      data=child_json,
                      content_type='application/json',
                      follow=1)
        assert res.status_code == 403

        # fix child permissions
        ebu_child.permission = 7
        ebu_child.save()

        # wrong parent
        child_json = {'site': site.pk,
                      'parent': 100023123123123,
                      'name': 'child name',
                      'path': 'test',
                      'is_active': 1}
        res = req.put(child_url,
                      data=child_json,
                      content_type='application/json',
                      follow=1)
        assert res.status_code == 404

        # wrong permissions on parent
        ebu_parent.permission = 3
        ebu_parent.save()
        child_json = {'site': site.pk,
                      'parent': parent.pk,
                      'name': 'child name',
                      'path': 'test',
                      'is_active': 1}
        res = req.put(child_url,
                      data=child_json,
                      content_type='application/json',
                      follow=1)
        assert res.status_code == 403

        # correct data and permissions on parent
        ebu_parent.permission = 7
        ebu_parent.save()

        # wrong alias
        child_json = {'site': site.pk,
                      'parent': parent.pk,
                      'name': 'child name',
                      'alias': 12312321,
                      'path': 'test',
                      'is_active': 1}
        res = req.put(child_url,
                      data=child_json,
                      content_type='application/json',
                      follow=1)
        assert res.status_code == 400

        # correct alias
        child_json = {'site': site.pk,
                      'parent': parent.pk,
                      'name': 'child name',
                      'alias': parent.pk,
                      'path': 'test',
                      'is_active': 1}
        res = req.put(child_url,
                      data=child_json,
                      content_type='application/json',
                      follow=1)
        child.refresh_from_db()
        assert child.alias == parent

        child_json = {'site': site.pk,
                      'parent': parent.pk,
                      'name': 'child name',
                      'alias': None,
                      'path': 'test',
                      'is_active': 1}
        res = req.put(child_url,
                      data=child_json,
                      content_type='application/json',
                      follow=1)
        child.refresh_from_db()
        assert isinstance(res.json(), dict)

        child_json = {'site': site.pk,
                      'parent': parent.pk,
                      'name': 'child name',
                      'alias': parent.pk,
                      'alias_url': 'https://www.unical.it',
                      'path': 'test',
                      'is_active': 1}
        res = req.put(child_url,
                      data=child_json,
                      content_type='application/json',
                      follow=1)
        child.refresh_from_db()
        assert child.alias_url == 'https://www.unical.it'

        child_json = {'site': site.pk,
                      'parent': parent.pk,
                      'name': 'child name',
                      'alias': parent.pk,
                      'alias_url': 'https://www.unical.it',
                      'path': 'test',
                      'is_active': 0}
        res = req.put(child_url,
                      data=child_json,
                      content_type='application/json',
                      follow=1)
        child.refresh_from_db()
        assert child.is_active == False

    def test_delete(self):
        req = Client()
        ebu = ContextUnitTest.create_editorialboard_user()
        webpath = ebu.webpath
        url = reverse('unicms_api:editorial-board-site-webpath',
                      kwargs={'site_id': webpath.site.pk,
                              'pk': webpath.pk})

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

    def test_post(self):
        req = Client()
        ebu_parent = ContextUnitTest.create_editorialboard_user()
        parent = ebu_parent.webpath

        # data with wrong parent
        data = {'site': parent.site.pk,
                'parent': 123123123213,
                'name': 'test webpath',
                'path': 'test',
                'is_active': 1}
        url = reverse('unicms_api:editorial-board-site-webpaths',
                      kwargs={'site_id': parent.site.pk})

        # accessible to staff users only
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert res.status_code == 403
        user = ebu_parent.user
        user.is_staff = True
        user.save()
        req.force_login(user)

        # no site
        data['site'] = None
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert res.status_code == 403
        data['site'] = parent.site.pk

        # no parent
        data['parent'] = None
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert res.status_code == 403
        data['parent'] = 123123123213

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
        assert res.status_code == 400

        # valid alias
        data['alias'] = parent.pk
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert WebPath.objects.filter(name='test webpath').first()
