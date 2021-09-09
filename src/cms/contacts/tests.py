import logging

from django.test import TestCase


from . models import Contact, ContactInfo, ContactInfoLocalization, ContactLocalization


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ContactUnitTest(TestCase):

    def setUp(cls):
        pass

    @classmethod
    def create_contact(cls, **kwargs):
        data = {'name': 'john doe',
                'description': 'employee of the year',
                'contact_type': 'person',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = Contact.objects.create(**data)
        return obj


    @classmethod
    def create_contact_info(cls, contact_data={}, **kwargs):
        if contact_data:
            contact = cls.create_contact(**contact_data)
        else:
            contact = cls.create_contact()
        data = {'contact': contact,
                'label': 'first email',
                'value': 'john.doe@email.com',
                'info_type': 'email',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = ContactInfo.objects.create(**data)
        return obj


    @classmethod
    def create_contact_localization(cls,
                                    contact_data={},
                                    **kwargs):
        contact = cls.create_contact(**contact_data)
        data = {'contact': contact,
                'language': 'en',
                'name': 'john doe en',
                'description': '',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = ContactLocalization.objects.create(**data)
        return obj


    @classmethod
    def create_contact_info_localization(cls,
                                         contact_data={},
                                         contact_info_data={},
                                         **kwargs):
        contact_info = cls.create_contact_info(contact_data=contact_data,
                                               **contact_info_data)
        data = {'contact_info': contact_info,
                'language': 'en',
                'label': 'first email en',
                'value': 'john.doe.en@email.com',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = ContactInfoLocalization.objects.create(**data)
        return obj

    def test_contact_localization(self):
        contact_info_localization = self.create_contact_info_localization()
        contact_info_localization.__str__()

        contact_info = contact_info_localization.contact_info
        contact = contact_info.contact
        contact.__str__()
        contact.localized()
        contact.get_infos()
