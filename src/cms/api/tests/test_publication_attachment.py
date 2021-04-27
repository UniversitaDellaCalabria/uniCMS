import logging
import os

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.test.client import encode_multipart
from django.urls import reverse

from cms.contexts.tests import ContextUnitTest



from cms.publications.models import Publication, PublicationAttachment
from cms.publications.tests import PublicationUnitTest

from glob import glob


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PublicationAttachmentAPIUnitTest(TestCase):

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
        url = reverse('unicms_api:editorial-board-publication-attachments',
                      kwargs={'publication_id': pub.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.is_superuser = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

        # POST
        data = {'publication': pub.pk,
                'name': 'test attachment',
                'description': 'test desc',
        }
        path = f'{settings.MEDIA_ROOT}/images/categories/eventi.jpg'
        img_file = open(path,'rb')
        data['file'] = img_file
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data,
                       follow=1)
        assert res.status_code == 403
        # user has permission
        img_file.seek(0)
        req.force_login(user)
        res = req.post(url, data=data, follow=1)
        attachment = PublicationAttachment.objects.filter(publication=pub,
                                                          name='test attachment').first()
        assert(attachment)

        # GET LOGS
        url = reverse('unicms_api:editorial-board-publication-attachment-logs',
                      kwargs={'publication_id': pub.pk,
                              'pk': attachment.pk})
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-publication-attachment',
                      kwargs={'publication_id': pub.pk,
                              'pk': attachment.pk})

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
        attachment.refresh_from_db()
        assert attachment.name == 'patched'

        # PUT
        img_file.seek(0)
        pub.created_by = None
        pub.save()
        data = {'publication': pub.pk,
                'name': 'test putted',
                'description': 'test desc',
                'file': img_file
        }
        content = encode_multipart('put_data', data)
        content_type = 'multipart/form-data; boundary=put_data'
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, content, content_type=content_type)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, content, content_type=content_type)
        attachment.refresh_from_db()
        assert attachment.name == 'test putted'

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            attachment.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:editorial-board-publication-attachment-form',
                      kwargs={'publication_id': pub.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)

    def tearDown(self):
        match = f'{settings.MEDIA_ROOT}/publications_attachments/*/eventi_*.*'
        for i in glob(match):
            os.remove(i)
