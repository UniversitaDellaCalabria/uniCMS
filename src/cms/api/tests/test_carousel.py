import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.carousels.models import Carousel
from cms.carousels.tests import CarouselUnitTest

from cms.contexts.tests import ContextUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CarouselAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_carousel(self):
        """
        Carousel API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        carousel = CarouselUnitTest.create_carousel()

        # carousel list
        url = reverse('unicms_api:carousels')

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
        data = {'name': 'posted name',
                'description': 'posted description',
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.post(url, data=data, follow=1)
        assert Carousel.objects.filter(name='posted name').first()

        # GET LOGS
        url = reverse('unicms_api:carousel-logs', kwargs={'pk': carousel.pk})
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # redis lock set
        ct = ContentType.objects.get_for_model(carousel)
        data = {'content_type_id': ct.pk,
                'object_id': carousel.pk}
        res = req.post(url, data,
                       content_type='application/json', follow=1)
        assert isinstance(res.json(), dict)

        # GET, patch, put, delete
        url = reverse('unicms_api:carousel', kwargs={'pk': carousel.pk})

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
        carousel.refresh_from_db()
        assert carousel.name == 'patched'

        # PUT
        carousel.created_by = None
        carousel.save()
        data = {'name': 'carousel api-test',
                'description': 'put description',
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, content_type='application/json')
        carousel.refresh_from_db()
        assert carousel.name == 'carousel api-test'
        assert not carousel.is_active

        # GET SelectField Options
        url = reverse('unicms_api:carousel-options')
        res = req.get(url)
        assert isinstance(res.json(), dict)

        url = reverse('unicms_api:carousel-option',
                      kwargs={'pk': carousel.pk})
        res = req.get(url)
        assert isinstance(res.json(), dict)

        # DELETE
        # user hasn't permission
        url = reverse('unicms_api:carousel', kwargs={'pk': carousel.pk})
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            carousel.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:carousel-form')
        res = req.get(url)
        assert isinstance(res.json(), list)
