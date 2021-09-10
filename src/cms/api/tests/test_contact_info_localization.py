import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.contacts.models import Contact, ContactInfoLocalization
from cms.contacts.tests import ContactUnitTest

from cms.contexts.tests import ContextUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ContactInfoLocalizationAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_contact_info_localization(self):
        """
        Contact Info Localization API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        contact_info_localization = ContactUnitTest.create_contact_info_localization()
        contact_info = contact_info_localization.contact_info
        contact = contact_info.contact

        # test if contact is locable by user
        contact_info_localization.is_lockable_by(user)

        # contact list
        url = reverse('unicms_api:contact-info-localizations',
                      kwargs={'contact_id': contact.pk,
                              'contact_info_id': contact_info.pk})

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
        data = {'contact_info': contact_info.pk,
                'language': 'en',
                'label': 'posted label',
                'value': contact_info_localization.value,
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        # wrong contact item
        contact_info_2 = ContactUnitTest.create_contact_info(contact=contact)
        data['contact_info'] = contact_info_2.pk
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 400
        # wrong contact_info
        data['contact_info'] = 11121
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 400
        data['contact_info'] = contact_info.pk
        # wrong parent contact
        url = reverse('unicms_api:contact-info-localizations',
                      kwargs={'contact_id': 12321321,
                              'contact_info_id': contact_info.pk})
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 400
        url = reverse('unicms_api:contact-info-localizations',
                      kwargs={'contact_id': contact.pk,
                              'contact_info_id': contact_info.pk})
        res = req.post(url, data=data, follow=1)
        assert ContactInfoLocalization.objects.filter(label='posted label').first()

        # GET LOGS
        url = reverse('unicms_api:contact-info-localization-logs',
                      kwargs={'contact_id': contact.pk,
                              'contact_info_id': contact_info.pk,
                              'pk': contact_info_localization.pk})
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # redis lock set
        ct = ContentType.objects.get_for_model(contact_info_localization)
        data = {'content_type_id': ct.pk,
                'object_id': contact_info_localization.pk}
        res = req.post(url, data,
                       content_type='application/json', follow=1)
        assert isinstance(res.json(), dict)

        # GET, patch, put, delete
        url = reverse('unicms_api:contact-info-localization',
                      kwargs={'contact_id': contact.pk,
                              'contact_info_id': contact_info.pk,
                              'pk': contact_info_localization.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        # wrong parent contact
        data = {'contact_info': 11121}
        res = req.patch(url, data=data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 400
        # correct data
        data = {'label': 'patched'}
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
        contact_info_localization.refresh_from_db()
        assert contact_info_localization.label == 'patched'

        # PUT
        contact.created_by = None
        contact.save()
        data = {'contact_info': contact_info.pk,
                'language': 'en',
                'label': 'putted label',
                'value': 'new value',
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, content_type='application/json')
        contact_info_localization.refresh_from_db()
        assert contact_info_localization.label == 'putted label'
        assert not contact_info_localization.is_active

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            contact_info_localization.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:contact-info-localization-form',
                      kwargs={'contact_id': contact.pk,
                              'contact_info_id': contact_info.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)
