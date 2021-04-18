import logging

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.test.client import encode_multipart
from django.urls import reverse

from cms.contexts.tests import ContextUnitTest

from cms.medias.models import Media
from cms.medias.tests import MediaUnitTest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MediaAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_media(self):
        """
        Media API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)

        # media list
        MediaUnitTest.create_media()
        url = reverse('unicms_api:medias')

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

        # media data
        path = f'{settings.MEDIA_ROOT}/images/categories/eventi.jpg'

        data = {'title': 'media1 api-test',
                'description': 'blah blah',
                'is_active': 1}
        url = reverse('unicms_api:medias')

        # accessible to staff users only
        res = req.post(url, data=data,
                       content_type='application/json', follow=1)
        assert res.status_code == 403
        user.is_staff = True
        user.is_superuser = True
        user.save()
        req.force_login(user)

        # POST
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

        # GET, patch, put, delete
        url = reverse('unicms_api:media', kwargs={'pk': media.pk})

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

        # PUT
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

        # GET SelectField Options
        url = reverse('unicms_api:media-options')
        res = req.get(url)
        assert isinstance(res.json(), dict)

        url = reverse('unicms_api:media-option',
                      kwargs={'pk': media.pk})
        res = req.get(url)
        assert isinstance(res.json(), dict)

        # DELETE
        url = reverse('unicms_api:media', kwargs={'pk': media.pk})
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

        # form
        url = reverse('unicms_api:media-form')
        res = req.get(url)
        assert isinstance(res.json(), list)
