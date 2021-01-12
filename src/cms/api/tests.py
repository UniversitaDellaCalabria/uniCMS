import logging

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.client import encode_multipart
from django.urls import reverse

from cms.contexts.models import WebPath
from cms.contexts.tests import ContextUnitTest

from cms.medias.models import Media
from cms.medias.tests import MediaUnitTest

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

    def test_webpath_edit(self):
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

        parent_url = reverse('unicms_api:editorial-board-site-webpath-view',
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
        child_url = reverse('unicms_api:editorial-board-site-webpath-view',
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

        # patch method not allowed
        res = req.patch(parent_url,
                        data={},
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 405

    def test_webpath_delete(self):
        req = Client()
        ebu = ContextUnitTest.create_editorialboard_user()
        webpath = ebu.webpath
        url = reverse('unicms_api:editorial-board-site-webpath-view',
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

    def test_webpath_new(self):
        req = Client()
        ebu_parent = ContextUnitTest.create_editorialboard_user()
        parent = ebu_parent.webpath

        # data with wrong parent
        data = {'site': parent.site.pk,
                'parent': 123123123213,
                'name': 'test webpath',
                'path': 'test',
                'is_active': 1}
        url = reverse('unicms_api:editorial-board-site-webpath-list',
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
        assert res.status_code == 404
        data['site'] = parent.site.pk

        # no parent
        data['parent'] = None
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert res.status_code == 404
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

    def test_media_list(self):
        req = Client()
        media = MediaUnitTest.create_media()
        user = ContextUnitTest.create_user()

        url = reverse('unicms_api:media-list')

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

    def test_media(self):
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        # media data
        path = f'{settings.MEDIA_ROOT}/images/categories/eventi.jpg'

        data = {'title': 'media1 api-test',
                'description': 'blah blah',
                'is_active': 1}
        url = reverse('unicms_api:media-list')

        # accessible to staff users only
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert res.status_code == 403
        user.is_staff = True
        user.is_superuser = True
        user.save()
        req.force_login(user)

        # create
        img_file = open(path,'rb')
        data['file'] = img_file
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        img_file.seek(0)
        res = req.post(url, data=data, follow=1)
        media = Media.objects.filter(title='media1 api-test').first()
        assert media.file

        # get, patch, put, delete
        url = reverse('unicms_api:media-view', kwargs={'pk': media.pk})

        # get
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # patch
        data = {'title': 'patched'}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has permission
        media.created_by = user2
        media.save()
        content_type = ContentType.objects.get_for_model(Media)
        edit_perm = Permission.objects.get(content_type=content_type, codename='change_media')
        user2.user_permissions.add(edit_perm)
        user2.refresh_from_db()
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        media.refresh_from_db()
        assert media.title == 'patched'

        # put
        media.created_by = None
        media.save()
        img_file.seek(0)
        data = {'title': 'media1 api-test',
                'description': 'put',
                'file': img_file,
                'is_active': 0}
        content = encode_multipart('put_data', data)
        content_type = 'multipart/form-data; boundary=put_data'
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, content, content_type=content_type)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, content, content_type=content_type)
        media.refresh_from_db()
        assert media.title == 'media1 api-test'
        assert not media.is_active

        # delete
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            media.refresh_from_db()
        except ObjectDoesNotExist:
            assert True
