import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.test.client import encode_multipart
from django.urls import reverse

from cms.carousels.models import Carousel, CarouselItemLocalization
from cms.carousels.tests import CarouselUnitTest

from cms.contexts.tests import ContextUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CarouselItemLocalizationAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_carousel_item_localization(self):
        """
        Carousel Item Localization API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        carousel_item_localization = CarouselUnitTest.create_carousel_item_localization()
        carousel_item = carousel_item_localization.carousel_item
        carousel = carousel_item.carousel
        # carousel list
        url = reverse('unicms_api:carousel-item-localizations',
                      kwargs={'carousel_id': carousel.pk,
                              'carousel_item_id': carousel_item.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.is_superuser = True
        user.save()
        req.force_login(user)
        res = req.get(url, {'is_active': True})
        assert isinstance(res.json(), dict)

        # POST
        data = {'carousel_item': carousel_item.pk,
                'language': 'en',
                'pre_heading': 'posted pre_heading',
                'heading': carousel_item_localization.heading,
                'description': carousel_item_localization.description,
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        # wrong carousel_item
        data['carousel_item'] = 11121
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        data['carousel_item'] = carousel_item.pk
        # wrong parent carousel
        url = reverse('unicms_api:carousel-item-localizations',
                      kwargs={'carousel_id': 12321321,
                              'carousel_item_id': carousel_item.pk})
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 404
        url = reverse('unicms_api:carousel-item-localizations',
                      kwargs={'carousel_id': carousel.pk,
                              'carousel_item_id': carousel_item.pk})
        res = req.post(url, data=data, follow=1)
        assert CarouselItemLocalization.objects.filter(pre_heading='posted pre_heading').first()

        # GET, patch, put, delete
        url = reverse('unicms_api:carousel-item-localization',
                      kwargs={'carousel_id': carousel.pk,
                              'carousel_item_id': carousel_item.pk,
                              'pk': carousel_item_localization.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        # wrong parent carousel
        data = {'carousel_item': 11121}
        res = req.patch(url, data=data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # correct data
        data = {'pre_heading': 'patched'}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has permission
        carousel.created_by = user2
        carousel.save()
        content_type = ContentType.objects.get_for_model(Carousel)
        edit_perm = Permission.objects.get(content_type=content_type, codename='change_carousel')
        user2.user_permissions.add(edit_perm)
        user2.refresh_from_db()
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        carousel_item_localization.refresh_from_db()
        assert carousel_item_localization.pre_heading == 'patched'

        # PUT
        carousel.created_by = None
        carousel.save()
        data = {'carousel_item': carousel_item.pk,
                'language': 'en',
                'pre_heading': 'putted pre_heading',
                'heading': carousel_item_localization.heading,
                'description': carousel_item_localization.description,
                'is_active': 0}
        content = encode_multipart('put_data', data)
        content_type = 'multipart/form-data; boundary=put_data'
        # wrong carousel item id
        data['carousel_item'] = 1221321312
        res = req.put(url, data,
                      content_type='application/json',
                      follow=1)
        assert res.status_code == 403
        data['carousel_item'] = carousel_item.pk
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, content, content_type=content_type)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, content, content_type=content_type)
        carousel_item_localization.refresh_from_db()
        assert carousel_item_localization.pre_heading == 'putted pre_heading'
        assert not carousel_item_localization.is_active

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            carousel_item_localization.refresh_from_db()
        except ObjectDoesNotExist:
            assert True
