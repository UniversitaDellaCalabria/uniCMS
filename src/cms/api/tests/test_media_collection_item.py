import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.contexts.tests import ContextUnitTest

from cms.medias.models import MediaCollection, MediaCollectionItem
from cms.medias.tests import MediaUnitTest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MediaCollectionItemAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_media_collection_item(self):
        """
        Media API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)

        # media list
        collection = MediaUnitTest.create_media_collection()
        media = MediaUnitTest.create_media()
        url = reverse('unicms_api:media-collection-items',
                      kwargs={'collection_id': collection.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

        # wrong item data
        data = {'media': media.pk,
                'collection': 21231231,
                'is_active': 1}

        # accessible to staff users only
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert res.status_code == 400
        user.is_staff = True
        user.is_superuser = True
        user.save()
        req.force_login(user)

        # POST
        # wrong data
        res = req.post(url, data=data,
                       content_type='application/json',
                       follow=1)
        assert res.status_code == 400
        # wrong collection
        collection_2 = MediaUnitTest.create_media_collection()
        data['collection'] = collection_2.pk
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert res.status_code == 400
        # correct data but...
        data['collection'] = collection.pk
        # ...user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data,
                       content_type='application/json',
                       follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.post(url, data=data,
                       content_type='application/json',
                       follow=1)
        item = MediaCollectionItem.objects.filter(media=media, collection=collection).first()
        assert item

        # GET LOGS
        url = reverse('unicms_api:media-collection-item-logs',
                      kwargs={'collection_id': collection.pk,
                              'pk': item.pk})
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # GET, patch, put, delete
        url = reverse('unicms_api:media-collection-item',
                      kwargs={'collection_id': collection.pk,
                              'pk': item.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        data = {'is_active': 0}
        # wrong collection
        data['collection'] = 12312312
        res = req.patch(url, data=data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 400
        # correct data but...
        data['collection'] = collection.pk
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
        item.refresh_from_db()
        assert not item.is_active

        # PUT
        collection.created_by = None
        collection.save()
        media2 = MediaUnitTest.create_media()
        data = {'media': media2.pk,
                'is_active': 1}
        # correct collection but...
        data['collection'] = collection.pk
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, content_type='application/json')
        item.refresh_from_db()
        assert item.media == media2
        assert item.is_active

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            item.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:media-collection-item-form',
                      kwargs={'collection_id': collection.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)
