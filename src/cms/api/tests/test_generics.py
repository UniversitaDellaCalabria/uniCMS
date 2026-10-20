import logging

from django import forms
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import reverse

from cms.api.serializers import UniCMSFormSerializer
from cms.api.utils import check_user_permission_on_object

from cms.carousels.models import Carousel, CarouselItem

from cms.contexts.models import EditorialBoardLock, EditorialBoardLockUser

from cms.pages.models import PageCarousel
from cms.pages.serializers import PageSerializer

from rest_framework.exceptions import ValidationError

# helpers imported as modules: their TestCases would run again here
from cms.carousels import tests as carousels_tests
from cms.contexts import tests as contexts_tests
from cms.medias import tests as medias_tests
from cms.pages import tests as pages_tests


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GenericViewsAPIUnitTest(TestCase):

    def setUp(self):
        self.req = Client()
        self.user = contexts_tests.ContextUnitTest.create_user(username='super',
                                                is_staff=True,
                                                is_superuser=True)
        self.req.force_login(self.user)

    def test_create_invalid_data(self):
        url = reverse('unicms_api:carousels')
        res = self.req.post(url, {'description': 'no name'},
                            content_type='application/json')
        assert res.status_code == 400
        assert not Carousel.objects.filter(description='no name').exists()

    def test_update_invalid_data(self):
        carousel = carousels_tests.CarouselUnitTest.create_carousel()
        url = reverse('unicms_api:carousel', kwargs={'pk': carousel.pk})
        res = self.req.patch(url, {'is_active': 'not a boolean'},
                             content_type='application/json')
        assert res.status_code == 400
        res = self.req.put(url, {'description': 'no name'},
                           content_type='application/json')
        assert res.status_code == 400
        carousel.refresh_from_db()
        assert carousel.description == 'blah blah'

    def test_delete_protected(self):
        page = pages_tests.PageUnitTest.create_page()
        carousel = PageCarousel.objects.get(page=page).carousel
        url = reverse('unicms_api:carousel', kwargs={'pk': carousel.pk})
        res = self.req.delete(url)
        # used by a page: protected
        assert res.status_code == 403
        assert 'cannot be deleted' in res.json()['detail']
        assert Carousel.objects.filter(pk=carousel.pk).exists()

    def test_stable_ordering_with_order_field(self):
        carousel = carousels_tests.CarouselUnitTest.create_carousel()
        media = medias_tests.MediaUnitTest.create_media()
        for order in (2, 1, 3):
            CarouselItem.objects.create(carousel=carousel, image=media,
                                        heading=f'item {order}',
                                        order=order, is_active=True)
        url = reverse('unicms_api:carousel-items',
                      kwargs={'carousel_id': carousel.pk})
        res = self.req.get(url, {'ordering': '-is_active'})
        assert res.status_code == 200
        # same is_active value: ordered by "order" field
        headings = [i['heading'] for i in res.json()['results']]
        assert headings == ['item 1', 'item 2', 'item 3']


class SafePermissionsAPIUnitTest(TestCase):

    def test_unsafe_methods(self):
        collection = medias_tests.MediaUnitTest.create_media_collection()
        url = reverse('unicms_api:media-collection-public-items',
                      kwargs={'collection_id': collection.pk})
        req = Client()
        # safe method allowed to everyone
        assert req.get(url).status_code == 200
        # unsafe methods allowed to staff and superusers only
        assert req.post(url, {}).status_code == 403
        staff = contexts_tests.ContextUnitTest.create_user(username='staff',
                                                           is_staff=True)
        req.force_login(staff)
        # permission granted, method not allowed
        assert req.post(url, {}).status_code == 405
        superuser = contexts_tests.ContextUnitTest.create_user(username='super',
                                                is_superuser=True)
        req.force_login(superuser)
        assert req.post(url, {}).status_code == 405

    def test_publication_get_create_permissions(self):
        url = reverse('unicms_api:editorial-board-publications')
        staff = contexts_tests.ContextUnitTest.create_user(username='staff',
                                                           is_staff=True)
        req = Client()
        req.force_login(staff)
        # staff can read
        assert req.get(url).status_code == 200
        # but can't create without Django permissions
        assert req.post(url, {}).status_code == 403


class UserPermissionOnObjectUnitTest(TestCase):

    def test_locks(self):
        owner = contexts_tests.ContextUnitTest.create_user(username='owner',
                                                           is_staff=True)
        carousel = carousels_tests.CarouselUnitTest.create_carousel(created_by=owner)
        user = contexts_tests.ContextUnitTest.create_user(username='editor',
                                                          is_staff=True)
        user.user_permissions.add(Permission.objects.get(codename='change_carousel'))
        # not owner and no locks
        assert check_user_permission_on_object(user, carousel) == {'granted': False}
        # object locked for another user
        lock = EditorialBoardLock.objects.create(
            content_type=ContentType.objects.get_for_model(carousel),
            object_id=carousel.pk
        )
        EditorialBoardLockUser.objects.create(lock=lock, user=owner)
        user = type(user).objects.get(pk=user.pk)
        assert check_user_permission_on_object(user, carousel) == {'granted': False,
                                                                   'locked': True}
        # object locked for user
        EditorialBoardLockUser.objects.create(lock=lock, user=user)
        assert check_user_permission_on_object(user, carousel) == {'granted': True,
                                                                   'locked': True}


class UniCMSSerializersUnitTest(TestCase):

    def test_form_serializer_widgets(self):
        class TestForm(forms.Form):
            day = forms.DateField()
            when = forms.DateTimeField()
            choices = forms.MultipleChoiceField(choices=(('a', 'A'),
                                                         ('b', 'B')))

        fields = {i['id']: i for i in UniCMSFormSerializer.serialize(TestForm())}
        assert fields['day']['type'] == 'date'
        assert fields['when']['type'] == 'datetime'
        assert fields['choices']['type'] == 'select'
        assert fields['choices']['multiple'] == 1
        assert fields['choices']['options'] == [{'text': 'A', 'value': 'a'},
                                                {'text': 'B', 'value': 'b'}]

    def test_tags_validator(self):
        serializer = PageSerializer()
        assert serializer.validate_tags(['tag']) == ['tag']
        # tags field is required
        with self.assertRaises(ValidationError):
            serializer.validate_tags([])
