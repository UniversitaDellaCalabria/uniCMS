import logging

from unittest import mock

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.contexts.models import AUTH_USER_GROUPS
from cms.contexts.tests import ContextUnitTest

from cms.pages.tests import PageUnitTest

from cms.publications.models import Publication
from cms.publications.tests import PublicationUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PublicationAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_publication(self):
        """
        Publication API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        pub = PublicationUnitTest.create_pub()

        # pulication list
        url = reverse('unicms_api:editorial-board-publications')

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.is_superuser = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

        category = PageUnitTest.create_category()

        # POST
        data = {'category': [category.pk],
                'name':'test api pub',
                'title':'test api pub',
                'subheading':'test',
                'content':'<p>test</p>',
                'content_type': 'html',
                'preview_image': '',
                'presentation_image': '',
                'note':'',
                'relevance':'0',
                'tags': ["hi","tag"],
                'is_active': True
        }
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.post(url, data=data, follow=1,
                       content_type='application/json')
        assert Publication.objects.filter(title='test api pub').first()

        # change state
        url = reverse('unicms_api:editorial-board-publication-change-status',
                      kwargs={'pk': pub.pk})
        req.force_login(user2)
        res = req.get(url, data,
                      content_type='application/json',
                      follow=1)
        assert res.status_code == 403
        # user has permission
        state = pub.is_active
        req.force_login(user)
        res = req.get(url, data,
                      content_type='application/json',
                      follow=1)
        pub.refresh_from_db()
        assert pub.is_active != state

        # GET LOGS
        url = reverse('unicms_api:editorial-board-publication-logs',
                      kwargs={'pk': pub.pk})
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-publication',
                      kwargs={'pk': pub.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        data = {'title': 'patched',
                'is_active': False}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has permission
        pub.created_by = user2
        pub.save()
        content_type = ContentType.objects.get_for_model(Publication)
        edit_perm = Permission.objects.get(content_type=content_type, codename='change_publication')
        user2.user_permissions.add(edit_perm)
        user2.refresh_from_db()
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        pub.refresh_from_db()
        assert pub.title == 'patched'

        # PUT
        pub.created_by = None
        pub.save()
        data = {'category': [category.pk],
                'name':'putted',
                'title':'putted',
                'subheading':'test',
                'content':'<p>putted</p>',
                'content_type': 'html',
                'preview_image': '',
                'presentation_image': '',
                'note':'',
                'relevance':'0',
                'tags': ["hi","tag"],
                'is_active': True
        }
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, content_type='application/json')
        pub.refresh_from_db()
        assert pub.title == 'putted'

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            pub.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # GET SelectField Options
        url = reverse('unicms_api:editorial-board-publications-options')
        res = req.get(url)
        assert isinstance(res.json(), dict)

        url = reverse('unicms_api:editorial-board-publications-option',
                      kwargs={'pk': pub.pk})
        res = req.get(url)
        assert isinstance(res.json(), dict)

        # form
        url = reverse('unicms_api:editorial-board-publication-form')
        res = req.get(url)
        assert isinstance(res.json(), list)

        # form
        url = reverse('unicms_api:editorial-board-publication-edit-form')
        res = req.get(url)
        assert isinstance(res.json(), list)



    def test_publications_by_context_category(self):
        pub = PublicationUnitTest.create_pub()
        webpath = pub.get_publication_context().webpath
        category = pub.category.first()
        url = reverse('unicms_api:api-news-by-contexts',
                      kwargs={'webpath_id': webpath.pk})
        req = Client()
        res = req.get(url, {'category': category.pk})
        assert res.status_code == 200
        assert res.json()['count'] == 4
        other_category = PageUnitTest.create_category(name='other')
        res = req.get(url, {'category': other_category.pk})
        assert res.json()['count'] == 0

    def test_publications_by_context_access_level(self):
        pub = PublicationUnitTest.create_pub()
        webpath = pub.get_publication_context().webpath
        url = reverse('unicms_api:api-news-by-contexts',
                      kwargs={'webpath_id': webpath.pk})
        req = Client()

        # registered users only
        webpath.access = '2'
        webpath.save()
        res = req.get(url)
        assert res.status_code in (401, 403)
        user = ContextUnitTest.create_user()
        req.force_login(user)
        res = req.get(url)
        assert res.status_code == 200
        assert res.json()['count'] == 4

        # custom access level (user attribute) configured in settings
        groups = AUTH_USER_GROUPS + (('is_staff', 'Staff users'),)
        with mock.patch('cms.contexts.models.AUTH_USER_GROUPS', groups):
            webpath.access = 'is_staff'
            webpath.save()
            res = req.get(url)
            assert res.status_code == 403
            user.is_staff = True
            user.save()
            res = req.get(url)
            assert res.status_code == 200

    def test_publication_patch_status(self):
        """
        an editor with change permission can also change
        the status of the publication
        """
        req = Client()
        user = ContextUnitTest.create_user(username='editor',
                                           is_staff=True)
        pub = PublicationUnitTest.create_pub(count=1)
        # owner of the publication
        pub.created_by = user
        pub.save()
        content_type = ContentType.objects.get_for_model(Publication)
        edit_perm = Permission.objects.get(content_type=content_type,
                                           codename='change_publication')
        user.user_permissions.add(edit_perm)
        req.force_login(user)
        url = reverse('unicms_api:editorial-board-publication',
                      kwargs={'pk': pub.pk})
        assert pub.is_active
        res = req.patch(url, {'is_active': False},
                        content_type='application/json')
        assert res.status_code == 200
        pub.refresh_from_db()
        assert not pub.is_active
