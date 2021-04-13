import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.carousels.models import Carousel, CarouselItemLink
from cms.carousels.tests import CarouselUnitTest

from cms.contexts.tests import ContextUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CarouselItemLinkAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_carousel_item_link(self):
        """
        Carousel Item Link API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        carousel_item_link = CarouselUnitTest.create_carousel_item_link()
        carousel_item = carousel_item_link.carousel_item
        carousel = carousel_item.carousel
        # carousel list
        url = reverse('unicms_api:carousel-item-links',
                      kwargs={'carousel_id': carousel.pk,
                              'carousel_item_id': carousel_item.pk})

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
        data = {'carousel_item': carousel_item.pk,
                'title_preset': carousel_item_link.title_preset,
                'title': 'posted title',
                'url': carousel_item_link.url,
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
        assert res.status_code == 400
        # wrong parent carousel
        carousel_item_2 = CarouselUnitTest.create_carousel_item()
        data['carousel_item'] = carousel_item_2.pk
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 400
        # correct data
        data['carousel_item'] = carousel_item.pk
        # wrong parent carousel
        url = reverse('unicms_api:carousel-item-links',
                      kwargs={'carousel_id': 12321321,
                              'carousel_item_id': carousel_item.pk})
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 400
        url = reverse('unicms_api:carousel-item-links',
                      kwargs={'carousel_id': carousel.pk,
                              'carousel_item_id': carousel_item.pk})
        res = req.post(url, data=data, follow=1)
        assert CarouselItemLink.objects.filter(title='posted title').first()

        # GET, patch, put, delete
        url = reverse('unicms_api:carousel-item-link',
                      kwargs={'carousel_id': carousel.pk,
                              'carousel_item_id': carousel_item.pk,
                              'pk': carousel_item_link.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        # wrong parent carousel
        data = {'carousel_item': 11121}
        res = req.patch(url, data=data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 400
        # correct data
        data = {'title': 'patched'}
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
        carousel_item_link.refresh_from_db()
        assert carousel_item_link.title == 'patched'

        # PUT
        carousel.created_by = None
        carousel.save()
        data = {'carousel_item': carousel_item.pk,
                'title_preset': carousel_item_link.title_preset,
                'title': 'putted title',
                'url': carousel_item_link.url,
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, content_type='application/json')
        carousel_item_link.refresh_from_db()
        assert carousel_item_link.title == 'putted title'
        assert not carousel_item_link.is_active

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            carousel_item_link.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:carousel-item-link-form',
                      kwargs={'carousel_id': carousel.pk,
                              'carousel_item_id': carousel_item.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)
