import logging

from django.test import TestCase

from cms.medias.tests import MediaUnitTest

from . models import Carousel, CarouselItem, CarouselItemLink, CarouselItemLinkLocalization, CarouselItemLocalization


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CarouselUnitTest(TestCase):

    def setUp(cls):
        pass

    @classmethod
    def create_carousel(cls, **kwargs):
        data = {'name': 'carousel1',
                'description': 'blah blah',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = Carousel.objects.create(**data)
        return obj


    @classmethod
    def create_carousel_item(cls, carousel_data={}, **kwargs):
        if carousel_data:
            carousel = cls.create_carousel(**carousel_data)
        else:
            carousel = cls.create_carousel()
        data = {'carousel': carousel,
                'heading': 'heading',
                'pre_heading': 'pre heading',
                'image': MediaUnitTest.create_media(),
                'description': 'blah blah',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = CarouselItem.objects.create(**data)
        return obj


    @classmethod
    def create_carousel_item_localization(cls,
                                  carousel_data={},
                                  carousel_data_item={},
                                  **kwargs):
        carousel_item = cls.create_carousel_item(carousel_data=carousel_data,
                                                  **carousel_data_item)
        data = {'carousel_item': carousel_item,
                'language': 'en',
                'pre_heading': 'pre heading eng',
                'heading': 'heading en',
                'description': '',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = CarouselItemLocalization.objects.create(**data)
        return obj


    @classmethod
    def create_carousel_item_link(cls,
                                  carousel_data={},
                                  carousel_data_item={},
                                  **kwargs):
        carousel_item = cls.create_carousel_item(carousel_data=carousel_data,
                                                 **carousel_data_item)
        data = {'carousel_item': carousel_item,
                'title': 'pre heading',
                'url': '/that/url',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = CarouselItemLink.objects.create(**data)
        return obj


    @classmethod
    def create_carousel_item_link_localization(cls,
                                               carousel_data={},
                                               carousel_data_item={},
                                               carousel_data_item_link={},
                                               **kwargs):
        carousel_item_link = cls.create_carousel_item_link(carousel_data=carousel_data,
                                                           carousel_data_item=carousel_data_item,
                                                           **carousel_data_item_link)
        data = {'carousel_item_link': carousel_item_link,
                'language': 'en',
                'title': 'title',
                'url': 'https://url.url',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = CarouselItemLinkLocalization.objects.create(**data)
        return obj


    def test_carousel_localization(self):
        carousel_item_localization = self.create_carousel_item_localization()
        carousel_item_localization.__str__()

        carousel_item = carousel_item_localization.carousel_item
        carousel = carousel_item.carousel
        carousel.__str__()

        carousel_item_link = CarouselItemLink.objects.create(**{'carousel_item': carousel_item,
                                                              'title': 'pre heading',
                                                              'url': '/that/url',
                                                              'is_active': 1})
        CarouselItemLinkLocalization.objects.create(**{'carousel_item_link': carousel_item_link,
                                                     'language': 'en',
                                                     'title': 'title',
                                                     'url': 'https://url.url',
                                                     'is_active': 1})
        carousel.get_items()

        carousel_item.__str__()
        carousel_item.get_links()
        carousel_item.localized(lang='en')


    def test_carousel_link(self):
        carousel_item_link = self.create_carousel_item_link()
        carousel_item_link.__str__()
        carousel_item_link.get_title()

        loc = CarouselItemLinkLocalization.\
                objects.create(carousel_item_link=carousel_item_link,
                               language = 'en',
                               title = 'title',
                               is_active = True)
        loc.__str__()


    # test template tags
    # def test_load_carousel(self):
        # needs page


# --- models, serializers, forms, template tags ---

from types import SimpleNamespace
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import RequestFactory, override_settings
from django.utils import timezone

from cms.medias.models import Media
from cms.medias.tests import TemporaryMediaRootMixin, make_upload

from . forms import (CarouselItemForm,
                     CarouselItemLinkForm,
                     CarouselItemLinkLocalizationForm,
                     CarouselItemLocalizationForm)
from . serializers import (CarouselForeignKey,
                           CarouselItemForeignKey,
                           CarouselItemLinkForeignKey,
                           CarouselItemLinkLocalizationSerializer,
                           CarouselItemLinkSerializer,
                           CarouselItemLocalizationSerializer,
                           CarouselItemSerializer,
                           CarouselSelectOptionsSerializer)
from . templatetags.unicms_carousels import load_carousel


CAROUSEL_TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {
        'loaders': [('django.template.loaders.locmem.Loader', {
            'carousel.html': '{% for i in carousel_items %}[{{ i.heading }}'
                             '{% for l in i.links %}|{{ l.title }}{% endfor %}]'
                             '{% endfor %}',
        })],
    },
}]


class CarouselBaseTest(TemporaryMediaRootMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.image = Media.objects.create(title='image', description='d',
                                          file=make_upload(name='image.png'))
        self.mobile = Media.objects.create(title='mobile', description='d',
                                           file=make_upload(name='mobile.png'))
        self.carousel = Carousel.objects.create(name='carousel', description='d',
                                                is_active=True)
        self.item = CarouselItem.objects.create(carousel=self.carousel, image=self.image,
                                                heading='heading', pre_heading='pre',
                                                description='desc', is_active=True)
        self.link = CarouselItemLink.objects.create(carousel_item=self.item,
                                                    title='link', url='/link',
                                                    is_active=True)


class CarouselModelsUnitTest(CarouselBaseTest):

    def test_get_items_publication_dates(self):
        now = timezone.localtime()
        CarouselItem.objects.create(carousel=self.carousel, image=self.image,
                                    heading='future', date_start=now + timezone.timedelta(days=1),
                                    is_active=True)
        CarouselItem.objects.create(carousel=self.carousel, image=self.image,
                                    heading='expired', date_end=now,
                                    is_active=True)
        CarouselItem.objects.create(carousel=self.carousel, image=self.image,
                                    heading='inactive', is_active=False)
        CarouselItem.objects.create(carousel=self.carousel, image=self.image,
                                    heading='running',
                                    date_start=now - timezone.timedelta(days=1),
                                    date_end=now + timezone.timedelta(days=1),
                                    is_active=True)
        items = self.carousel.get_items()
        self.assertEqual([i.heading for i in items], ['heading', 'running'])
        self.assertEqual([l.title for l in items[0].links], ['link'])

    def test_localized(self):
        CarouselItemLocalization.objects.create(carousel_item=self.item, language='it',
                                                heading='titolo', pre_heading='pre it',
                                                description='desc it',
                                                mobile_image=self.mobile,
                                                is_active=True)
        CarouselItemLinkLocalization.objects.create(carousel_item_link=self.link,
                                                    language='it', title='collegamento',
                                                    url='/it/link', is_active=True)
        item = self.carousel.get_items(lang='it')[0]
        self.assertEqual(item.heading, 'titolo')
        self.assertEqual(item.pre_heading, 'pre it')
        self.assertEqual(item.description, 'desc it')
        # localized image missing: original one is kept
        self.assertEqual(item.image, self.image)
        self.assertEqual(item.mobile_image, self.mobile)
        self.assertEqual(item.links[0].title, 'collegamento')
        self.assertEqual(item.links[0].url, '/it/link')
        # no localization
        item = self.carousel.get_items(lang='fr')[0]
        self.assertEqual(item.heading, 'heading')
        self.assertEqual(item.links[0].title, 'link')

    def test_link_title(self):
        self.assertEqual(self.link.get_title(), 'link')
        # preset label instead of custom title
        labels = dict(CarouselItemLink._meta.get_field('title_preset').choices)
        preset = next(k for k in labels if k != 'custom')
        self.link.title_preset = preset
        self.assertEqual(self.link.get_title(), labels[preset])

    def test_is_lockable_by(self):
        superuser = get_user_model().objects.create(username='su', is_superuser=True)
        user = get_user_model().objects.create(username='nobody')
        item_loc = CarouselItemLocalization.objects.create(carousel_item=self.item,
                                                           language='it')
        link_loc = CarouselItemLinkLocalization.objects.create(carousel_item_link=self.link,
                                                               language='it', url='/it')
        for obj in (self.item, self.link, item_loc, link_loc):
            self.assertTrue(obj.is_lockable_by(superuser))
            self.assertFalse(obj.is_lockable_by(user))
        self.assertEqual(str(self.item), '[carousel] heading')
        self.assertEqual(str(self.link), '[carousel] heading /link')
        self.assertEqual(str(item_loc), '[carousel] heading it')
        self.assertEqual(str(link_loc), 'carousel /link')


class CarouselSerializersUnitTest(CarouselBaseTest):

    def _bind(self, field_class, serializer_class, request=None):
        field = field_class()
        context = {'request': request} if request else {}
        field.bind('field', serializer_class(context=context))
        return field

    def test_foreign_keys(self):
        other = Carousel.objects.create(name='other', description='d')
        CarouselItem.objects.create(carousel=other, image=self.image)
        request = SimpleNamespace(parser_context={'kwargs': {
            'carousel_id': self.carousel.pk,
            'carousel_item_id': self.item.pk,
            'carousel_item_link_id': self.link.pk}})
        for field_class, serializer_class, expected in (
                (CarouselForeignKey, CarouselItemSerializer, [self.carousel]),
                (CarouselItemForeignKey, CarouselItemLinkSerializer, [self.item]),
                (CarouselItemLinkForeignKey, CarouselItemLinkLocalizationSerializer, [self.link])):
            self.assertIsNone(self._bind(field_class, serializer_class).get_queryset())
            field = self._bind(field_class, serializer_class, request)
            self.assertEqual(list(field.get_queryset()), expected)

    def test_item_serializer(self):
        data = CarouselItemSerializer(self.item).data
        self.assertEqual(data['image']['id'], self.image.pk)
        self.assertIsNone(data['mobile_image'])
        self.item.mobile_image = self.mobile
        data = CarouselItemSerializer(self.item).data
        self.assertEqual(data['mobile_image']['id'], self.mobile.pk)

    def test_item_serializer_empty_dates(self):
        request = SimpleNamespace(parser_context={'kwargs': {'carousel_id': self.carousel.pk}})
        data = {'carousel': self.carousel.pk, 'image': self.image.pk,
                'date_start': '', 'date_end': '', 'is_active': True}
        serializer = CarouselItemSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNone(serializer.validated_data['date_start'])
        self.assertIsNone(serializer.validated_data['date_end'])

    def test_localization_serializer(self):
        loc = CarouselItemLocalization.objects.create(carousel_item=self.item,
                                                      language='it')
        data = CarouselItemLocalizationSerializer(loc).data
        self.assertIsNone(data['image'])
        self.assertIsNone(data['mobile_image'])
        loc.image = self.image
        loc.mobile_image = self.mobile
        data = CarouselItemLocalizationSerializer(loc).data
        self.assertEqual(data['image']['id'], self.image.pk)
        self.assertEqual(data['mobile_image']['id'], self.mobile.pk)

    def test_select_options(self):
        self.assertEqual(CarouselSelectOptionsSerializer(self.carousel).data,
                         {'value': self.carousel.pk, 'text': 'carousel'})

    def test_forms(self):
        other = Carousel.objects.create(name='other', description='d')
        other_item = CarouselItem.objects.create(carousel=other, image=self.image)
        CarouselItemLink.objects.create(carousel_item=other_item, url='/other')

        form = CarouselItemForm(carousel_id=self.carousel.pk)
        self.assertEqual(list(form.fields['carousel'].queryset), [self.carousel])
        self.assertEqual(CarouselItemForm().fields['carousel'].queryset.count(), 2)

        kwargs = {'carousel_id': self.carousel.pk, 'carousel_item_id': self.item.pk}
        form = CarouselItemLocalizationForm(**kwargs)
        self.assertEqual(list(form.fields['carousel_item'].queryset), [self.item])
        self.assertEqual(CarouselItemLocalizationForm().fields['carousel_item'].queryset.count(), 2)

        form = CarouselItemLinkForm(**kwargs)
        self.assertEqual(list(form.fields['carousel_item'].queryset), [self.item])
        self.assertEqual(CarouselItemLinkForm().fields['carousel_item'].queryset.count(), 2)

        form = CarouselItemLinkLocalizationForm(carousel_item_link_id=self.link.pk, **kwargs)
        self.assertEqual(list(form.fields['carousel_item_link'].queryset), [self.link])
        self.assertEqual(CarouselItemLinkLocalizationForm().fields['carousel_item_link'].queryset.count(), 2)


@override_settings(TEMPLATES=CAROUSEL_TEMPLATES)
class CarouselTemplateTagsUnitTest(CarouselBaseTest):

    def setUp(self):
        super().setUp()
        self.request = RequestFactory().get('/')
        self.request.LANGUAGE_CODE = 'it'
        CarouselItemLocalization.objects.create(carousel_item=self.item, language='it',
                                                heading='titolo', is_active=True)

    def _page(self, page_carousel):
        page = mock.MagicMock()
        page.get_carousels.return_value.first.return_value = page_carousel
        return page

    def test_load_carousel_by_id(self):
        context = {'request': self.request, 'page': self._page(None)}
        self.assertEqual(load_carousel(context, None, 'carousel.html',
                                       carousel_id=self.carousel.pk),
                         '[titolo|link]')
        with self.assertLogs('cms.carousels.templatetags.unicms_carousels', level='ERROR'):
            self.assertEqual(load_carousel(context, None, 'carousel.html',
                                           carousel_id=9999), '')

    def test_load_carousel_by_section(self):
        page_carousel = SimpleNamespace(carousel=self.carousel)
        context = {'request': self.request, 'page': self._page(page_carousel)}
        self.assertEqual(load_carousel(context, 'banner', 'carousel.html'),
                         '[titolo|link]')
        # no section
        self.assertEqual(load_carousel(context, '', 'carousel.html'), '')
        # no carousel in page
        context['page'] = self._page(None)
        with self.assertLogs('cms.carousels.templatetags.unicms_carousels', level='ERROR'):
            self.assertEqual(load_carousel(context, 'banner', 'carousel.html'), '')
