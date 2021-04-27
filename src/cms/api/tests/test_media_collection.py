import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.contexts.tests import ContextUnitTest

from cms.medias.models import MediaCollection
from cms.medias.tests import MediaUnitTest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MediaCollectionAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_media_collection(self):
        """
        Media API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)

        # media list
        MediaUnitTest.create_media_collection()
        url = reverse('unicms_api:media-collections')

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

        # media data
        data = {'name': 'media collections api-test',
                'description': 'blah blah',
                'tags': '["test","unit"]',
                'is_active': 1}

        # accessible to staff users only
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert res.status_code == 403
        user.is_staff = True
        user.is_superuser = True
        user.save()
        req.force_login(user)

        # POST
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.post(url, data=data,
                       content_type='application/json',
                       follow=1)
        collection = MediaCollection.objects.filter(name='media collections api-test').first()
        assert collection

        # GET LOGS
        url = reverse('unicms_api:media-collection-logs',
                      kwargs={'pk': collection.pk})
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # GET, patch, put, delete
        url = reverse('unicms_api:media-collection',
                      kwargs={'pk': collection.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        data = {'name': 'patched'}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has permission
        collection.created_by = user2
        collection.save()
        content_type = ContentType.objects.get_for_model(MediaCollection)
        edit_perm = Permission.objects.get(content_type=content_type, codename='change_mediacollection')
        user2.user_permissions.add(edit_perm)
        user2.refresh_from_db()
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        collection.refresh_from_db()
        assert collection.name == 'patched'

        # PUT
        collection.created_by = None
        collection.save()
        data = {'name': 'media collection api-test',
                'description': 'put',
                'tags': ["hi","tag"],
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, content_type='application/json')
        collection.refresh_from_db()
        assert collection.description == 'put'
        assert not collection.is_active

        # GET SelectField Options
        url = reverse('unicms_api:media-collection-options')
        res = req.get(url)
        assert isinstance(res.json(), dict)

        url = reverse('unicms_api:media-collection-option',
                      kwargs={'pk': collection.pk})
        res = req.get(url)
        assert isinstance(res.json(), dict)

        # DELETE
        url = reverse('unicms_api:media-collection',
                      kwargs={'pk': collection.pk})
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            collection.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:media-collection-form')
        res = req.get(url)
        assert isinstance(res.json(), list)
