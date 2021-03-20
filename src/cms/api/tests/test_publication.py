import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

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
                'title':'test api pub',
                'subheading':'test',
                'content':'<p>test</p>',
                'content_type': 'html',
                'presentation_image': '',
                'note':'',
                'relevance':'0',
                'tags': ["hi","tag"],
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

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-publication',
                      kwargs={'pk': pub.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        data = {'title': 'patched'}
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
                'title':'putted',
                'subheading':'test',
                'content':'<p>putted</p>',
                'content_type': 'html',
                'presentation_image': '',
                'note':'',
                'relevance':'0',
                'tags': ["hi","tag"],
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

        # form
        url = reverse('unicms_api:editorial-board-publication-form')
        res = req.get(url)
        assert isinstance(res.json(), list)


