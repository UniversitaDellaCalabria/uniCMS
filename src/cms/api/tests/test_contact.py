import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.contacts.models import Contact
from cms.contacts.tests import ContactUnitTest

from cms.contexts.tests import ContextUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ContactAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_contact(self):
        """
        Contact API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        contact = ContactUnitTest.create_contact()

        # contact list
        url = reverse('unicms_api:contacts')

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
        data = {'name': 'John Doe',
                'description': 'posted description',
                'contact_type': 'person',
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.post(url, data=data, follow=1)
        assert Contact.objects.filter(name='John Doe').first()

        # GET LOGS
        url = reverse('unicms_api:contact-logs', kwargs={'pk': contact.pk})
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # redis lock set
        ct = ContentType.objects.get_for_model(contact)
        data = {'content_type_id': ct.pk,
                'object_id': contact.pk}
        res = req.post(url, data,
                       content_type='application/json', follow=1)
        assert isinstance(res.json(), dict)

        # GET, patch, put, delete
        url = reverse('unicms_api:contact', kwargs={'pk': contact.pk})

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
        contact.refresh_from_db()
        assert contact.name == 'patched'

        # PUT
        contact.created_by = None
        contact.save()
        data = {'name': 'contact api-test',
                'description': 'put description',
                'contact_type': 'person',
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, content_type='application/json')
        contact.refresh_from_db()
        assert contact.name == 'contact api-test'
        assert not contact.is_active

        # GET SelectField Options
        url = reverse('unicms_api:contact-options')
        res = req.get(url)
        assert isinstance(res.json(), dict)

        url = reverse('unicms_api:contact-option',
                      kwargs={'pk': contact.pk})
        res = req.get(url)
        assert isinstance(res.json(), dict)

        # DELETE
        # user hasn't permission
        url = reverse('unicms_api:contact', kwargs={'pk': contact.pk})
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            contact.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:contact-form')
        res = req.get(url)
        assert isinstance(res.json(), list)
