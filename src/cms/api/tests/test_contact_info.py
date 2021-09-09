import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.test.client import encode_multipart
from django.urls import reverse

from cms.contacts.models import Contact, ContactInfo
from cms.contacts.tests import ContactUnitTest

from cms.contexts.tests import ContextUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ContactInfoAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_contact_info(self):
        """
        Contact Info API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        contact_info = ContactUnitTest.create_contact_info()
        contact = contact_info.contact

        # contact list
        url = reverse('unicms_api:contact-infos',
                      kwargs={'contact_id': contact.pk})

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
        data = {'contact': contact.pk,
                'label': 'label',
                'value': 'posted value',
                'info_type': 'email',
                'is_active': 0}

        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        # wrong parent contact
        data['contact'] = 11121
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 400
        # wrong parent contact
        contact_2 = ContactUnitTest.create_contact()
        data['contact'] = contact_2.pk
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 400
        # correct data
        data['contact'] = contact.pk
        res = req.post(url, data=data, follow=1)
        assert ContactInfo.objects.filter(value='posted value').first()

        # GET LOGS
        url = reverse('unicms_api:contact-info-logs',
                      kwargs={'contact_id': contact.pk,
                              'pk': contact_info.pk})
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # redis lock set
        ct = ContentType.objects.get_for_model(contact_info)
        url = reverse('unicms_api:editorial-board-redis-lock-set')
        data = {'content_type_id': ct.pk,
                'object_id': contact_info.pk}
        res = req.post(url, data,
                       content_type='application/json', follow=1)
        assert isinstance(res.json(), dict)

        # GET, patch, put, delete
        url = reverse('unicms_api:contact-info',
                      kwargs={'contact_id': contact.pk,
                              'pk': contact_info.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        # wrong contact id
        data = {'contact': 1221321312}
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 400
        # patch contact id
        data = {'contact': contact_info.contact.pk}
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 200
        # correct data
        data = {'value': 'patched'}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has permission
        contact.created_by = user2
        contact.save()
        content_type = ContentType.objects.get_for_model(Contact)
        edit_perm = Permission.objects.get(content_type=content_type, codename='change_contact')
        user2.user_permissions.add(edit_perm)
        user2.refresh_from_db()
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        contact_info.refresh_from_db()
        assert contact_info.value == 'patched'

        # PUT
        contact.created_by = None
        contact.save()
        data = {'contact': contact_info.contact.pk,
                'label': 'label 2',
                'value': 'putted value',
                'info_type': 'email',
                'is_active': 0}
        content = encode_multipart('put_data', data)
        content_type = 'multipart/form-data; boundary=put_data'
        # wrong contact id
        data['contact'] = 1221321312
        res = req.put(url, data,
                      content_type='application/json',
                      follow=1)
        assert res.status_code == 400
        data['contact'] = contact.pk
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, content, content_type=content_type)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, content, content_type=content_type)
        contact_info.refresh_from_db()
        assert contact_info.value == 'putted value'
        assert not contact_info.is_active

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            contact_info.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # contact form
        url = reverse('unicms_api:contact-info-form',
                      kwargs={'contact_id': contact.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)

        url = reverse('unicms_api:contact-info-form-generic')
        res = req.get(url)
        assert isinstance(res.json(), list)
