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


# --- models, serializers, forms, template tags ---

from types import SimpleNamespace
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import RequestFactory, override_settings

from cms.medias.models import Media
from cms.medias.tests import TemporaryMediaRootMixin, make_upload

from . forms import (ContactForm,
                     ContactInfoForm,
                     ContactInfoLocalizationForm,
                     ContactLocalizationForm)
from . serializers import (ContactForeignKey,
                           ContactInfoForeignKey,
                           ContactInfoLocalizationSerializer,
                           ContactInfoSerializer,
                           ContactSelectOptionsSerializer,
                           ContactSerializer)
from . templatetags.unicms_contacts import load_contact


CONTACT_TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {
        'loaders': [('django.template.loaders.locmem.Loader', {
            'contact.html': '{{ contact.name }}{% for i in contact_infos %}'
                            '|{{ i.label }}:{{ i.value }}{% endfor %}',
        })],
    },
}]


class ContactBaseTest(TestCase):

    def setUp(self):
        super().setUp()
        self.contact = Contact.objects.create(name='john', contact_type='person',
                                              description='desc', is_active=True)
        self.info = ContactInfo.objects.create(contact=self.contact, info_type='email',
                                               label='email', value='john@example.org',
                                               is_active=True)
        self.request = RequestFactory().get('/')
        self.request.LANGUAGE_CODE = 'it'


class ContactModelsUnitTest(ContactBaseTest):

    def test_localized(self):
        ContactLocalization.objects.create(contact=self.contact, language='it',
                                           name='giovanni', description='descr',
                                           is_active=True)
        ContactInfoLocalization.objects.create(contact_info=self.info, language='it',
                                               label='posta', value='gio@example.org',
                                               is_active=True)
        ContactInfo.objects.create(contact=self.contact, info_type='phone',
                                   value='123', is_active=False)
        contact = Contact.objects.get(pk=self.contact.pk).localized(lang='it')
        self.assertEqual(contact.name, 'giovanni')
        self.assertEqual(contact.description, 'descr')
        infos = contact.get_infos(lang='it')
        self.assertEqual([(i.label, i.value) for i in infos],
                         [('posta', 'gio@example.org')])
        # no localization
        contact = Contact.objects.get(pk=self.contact.pk).localized(lang='fr')
        self.assertEqual(contact.name, 'john')
        self.assertEqual(contact.get_infos(lang='fr')[0].value, 'john@example.org')

    def test_clean_website(self):
        info = ContactInfo(contact=self.contact, info_type='website',
                           value='javascript:alert(1)')
        with self.assertRaises(ValidationError):
            info.clean()
        info.value = 'https://example.org'
        info.clean()
        # not a website: not validated as url
        info = ContactInfo(contact=self.contact, info_type='other',
                           value='javascript:alert(1)')
        info.clean()

        website = ContactInfo.objects.create(contact=self.contact, info_type='website',
                                             value='https://example.org')
        loc = ContactInfoLocalization(contact_info=website, language='it',
                                      value='javascript:alert(1)')
        with self.assertRaises(ValidationError):
            loc.clean()
        loc.value = 'https://example.org/it'
        loc.clean()
        # contact info not set yet
        ContactInfoLocalization(value='javascript:alert(1)').clean()

    def test_is_lockable_by(self):
        superuser = get_user_model().objects.create(username='su', is_superuser=True)
        user = get_user_model().objects.create(username='nobody')
        loc = ContactLocalization.objects.create(contact=self.contact, language='it')
        info_loc = ContactInfoLocalization.objects.create(contact_info=self.info,
                                                          language='it', value='v')
        for obj in (loc, self.info, info_loc):
            self.assertTrue(obj.is_lockable_by(superuser))
            self.assertFalse(obj.is_lockable_by(user))
        self.assertEqual(str(loc), 'john it')
        self.assertEqual(str(self.info), '[john] email: john@example.org')
        self.assertEqual(str(info_loc), '[john] email: john@example.org it')


class ContactSerializersUnitTest(TemporaryMediaRootMixin, ContactBaseTest):

    def _bind(self, field_class, serializer_class, request=None):
        field = field_class()
        context = {'request': request} if request else {}
        field.bind('field', serializer_class(context=context))
        return field

    def test_foreign_keys(self):
        other = Contact.objects.create(name='other', contact_type='person')
        ContactInfo.objects.create(contact=other, info_type='email', value='o@o.org')
        request = SimpleNamespace(parser_context={'kwargs': {
            'contact_id': self.contact.pk,
            'contact_info_id': self.info.pk}})
        for field_class, serializer_class, expected in (
                (ContactForeignKey, ContactInfoSerializer, [self.contact]),
                (ContactInfoForeignKey, ContactInfoLocalizationSerializer, [self.info])):
            self.assertIsNone(self._bind(field_class, serializer_class).get_queryset())
            field = self._bind(field_class, serializer_class, request)
            self.assertEqual(list(field.get_queryset()), expected)

    def test_contact_serializer(self):
        self.assertIsNone(ContactSerializer(self.contact).data['image'])
        image = Media.objects.create(title='image', description='d',
                                     file=make_upload())
        self.contact.image = image
        data = ContactSerializer(self.contact).data
        self.assertEqual(data['image']['id'], image.pk)

    def test_contact_info_serializer_website(self):
        request = SimpleNamespace(parser_context={'kwargs': {'contact_id': self.contact.pk}})
        context = {'request': request}
        data = {'contact': self.contact.pk, 'info_type': 'website',
                'value': 'javascript:alert(1)'}
        self.assertFalse(ContactInfoSerializer(data=data, context=context).is_valid())
        data['value'] = 'https://example.org'
        self.assertTrue(ContactInfoSerializer(data=data, context=context).is_valid())
        # partial update: info_type taken from the instance
        website = ContactInfo.objects.create(contact=self.contact, info_type='website',
                                             value='https://example.org')
        serializer = ContactInfoSerializer(website, data={'value': 'javascript:alert(1)'},
                                           partial=True, context=context)
        self.assertFalse(serializer.is_valid())
        serializer = ContactInfoSerializer(self.info, data={'value': 'x@example.org'},
                                           partial=True, context=context)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_contact_info_localization_serializer_website(self):
        website = ContactInfo.objects.create(contact=self.contact, info_type='website',
                                             value='https://example.org')
        request = SimpleNamespace(parser_context={'kwargs': {'contact_id': self.contact.pk,
                                                             'contact_info_id': website.pk}})
        context = {'request': request}
        data = {'contact_info': website.pk, 'language': 'it',
                'value': 'javascript:alert(1)'}
        self.assertFalse(ContactInfoLocalizationSerializer(data=data,
                                                           context=context).is_valid())
        data['value'] = 'https://example.org/it'
        self.assertTrue(ContactInfoLocalizationSerializer(data=data,
                                                          context=context).is_valid())
        # partial update: contact info taken from the instance
        loc = ContactInfoLocalization.objects.create(contact_info=website, language='it',
                                                     value='https://example.org/it')
        serializer = ContactInfoLocalizationSerializer(loc, data={'value': 'javascript:alert(1)'},
                                                       partial=True, context=context)
        self.assertFalse(serializer.is_valid())

    def test_select_options(self):
        self.assertEqual(ContactSelectOptionsSerializer(self.contact).data,
                         {'value': self.contact.pk, 'text': 'john'})

    def test_forms(self):
        other = Contact.objects.create(name='other', contact_type='person')
        ContactInfo.objects.create(contact=other, info_type='email', value='o@o.org')
        self.assertIn('image', ContactForm().fields)
        for form_class in (ContactInfoForm, ContactLocalizationForm):
            form = form_class(contact_id=self.contact.pk)
            self.assertEqual(list(form.fields['contact'].queryset), [self.contact])
            self.assertEqual(form_class().fields['contact'].queryset.count(), 2)
        form = ContactInfoLocalizationForm(contact_id=self.contact.pk,
                                           contact_info_id=self.info.pk)
        self.assertEqual(list(form.fields['contact_info'].queryset), [self.info])
        self.assertEqual(ContactInfoLocalizationForm().fields['contact_info'].queryset.count(), 2)


@override_settings(TEMPLATES=CONTACT_TEMPLATES)
class ContactTemplateTagsUnitTest(ContactBaseTest):

    def setUp(self):
        super().setUp()
        ContactLocalization.objects.create(contact=self.contact, language='it',
                                           name='giovanni', is_active=True)

    def _page(self, page_contact):
        page = mock.MagicMock()
        page.get_contacts.return_value.first.return_value = page_contact
        return page

    def test_load_contact_by_id(self):
        context = {'request': self.request, 'page': self._page(None)}
        self.assertEqual(load_contact(context, None, 'contact.html',
                                      contact_id=self.contact.pk),
                         'giovanni|email:john@example.org')
        with self.assertLogs('cms.contacts.templatetags.unicms_contacts', level='ERROR'):
            self.assertEqual(load_contact(context, None, 'contact.html',
                                          contact_id=9999), '')

    def test_load_contact_by_section(self):
        page_contact = SimpleNamespace(contact=self.contact)
        context = {'request': self.request, 'page': self._page(page_contact)}
        self.assertEqual(load_contact(context, '1-right-b', 'contact.html'),
                         'giovanni|email:john@example.org')
        # no section
        self.assertEqual(load_contact(context, '', 'contact.html'), '')
        # no contact in page
        context['page'] = self._page(None)
        with self.assertLogs('cms.contacts.templatetags.unicms_contacts', level='ERROR'):
            self.assertEqual(load_contact(context, '1-right-b', 'contact.html'), '')
