import logging

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.api.concurrency import LOCKS_CACHE_KEY_PREFIX, get_lock_from_cache

from cms.carousels.tests import CarouselUnitTest

from cms.contexts.models import EditorialBoardLockUser
from cms.contexts.tests import ContextUnitTest

from cms.pages.tests import PageUnitTest

from cms.publications.tests import PublicationUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EditorialBoardLockAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_lock(self):
        """
        Editorial Board Locks API
        """
        req = Client()
        user = ContextUnitTest.create_user(is_staff=True)
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)

        webpath = ContextUnitTest.create_webpath()
        webpath_ct = ContentType.objects.get_for_model(webpath)

        # webpath redis lock get
        url = reverse('unicms_api:editorial-board-redis-lock',
                      kwargs={'content_type_id': webpath_ct.pk,
                              'object_id': webpath.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_superuser = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

        # webpath redis redislocks set
        url = reverse('unicms_api:editorial-board-redis-lock-set')

        data = {'content_type_id': webpath_ct.pk,
                'object_id': webpath.pk}
        res = req.post(url, data,
                       content_type='application/json', follow=1)
        assert isinstance(res.json(), dict)

        # webpath locks list
        url = reverse('unicms_api:editorial-board-locks',
                      kwargs={'content_type_id': webpath_ct.pk,
                              'object_id': webpath.pk})

        res = req.get(url)
        assert res.data['count'] == 0

        # POST
        data = {'user': user.pk}
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.post(url, data=data, follow=1)
        lock = EditorialBoardLockUser.objects.filter(lock__content_type=webpath_ct,
                                                     lock__object_id=webpath.pk,
                                                     user=user).first()
        assert lock

        res = req.post(url, data=data, follow=1)
        assert res.status_code == 400

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-lock-delete',
                      kwargs={'content_type_id': webpath_ct.pk,
                              'object_id': webpath.pk,
                              'pk': lock.pk})

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            lock.refresh_from_db()
        except ObjectDoesNotExist:
            assert True


        # carousel test
        carousel = CarouselUnitTest.create_carousel()
        carousel_ct = ContentType.objects.get_for_model(carousel)

        # POST
        url = reverse('unicms_api:editorial-board-locks',
                      kwargs={'content_type_id': carousel_ct.pk,
                              'object_id': carousel.pk})
        data = {'user': user.pk}
        # user has permission
        req.force_login(user)
        res = req.post(url, data=data, follow=1)
        carousel_lock = EditorialBoardLockUser.objects.filter(lock__content_type=carousel_ct,
                                                              lock__object_id=carousel.pk,
                                                              user=user).first()
        assert carousel_lock

        # test other objects not inheriting is_lockable() method
        data = {'user': user.pk}
        req.force_login(user)

        page = PageUnitTest.create_page()
        page_ct = ContentType.objects.get_for_model(page)

        url = reverse('unicms_api:editorial-board-locks',
                      kwargs={'content_type_id': page_ct.pk,
                              'object_id': page.pk})

        # POST
        res = req.post(url, data=data, follow=1)
        lock = EditorialBoardLockUser.objects.filter(lock__content_type=page_ct,
                                                     lock__object_id=page.pk,
                                                     user=user).first()
        assert lock

        publication = PublicationUnitTest.create_pub()
        publication_ct = ContentType.objects.get_for_model(publication)

        url = reverse('unicms_api:editorial-board-locks',
                      kwargs={'content_type_id': publication_ct.pk,
                              'object_id': publication.pk})

        # POST
        res = req.post(url, data=data, follow=1)
        lock = EditorialBoardLockUser.objects.filter(lock__content_type=publication_ct,
                                                     lock__object_id=publication.pk,
                                                     user=user).first()
        assert lock


class RedisLockAPIUnitTest(TestCase):

    def setUp(self):
        self.req = Client()
        self.webpath = ContextUnitTest.create_webpath()
        self.ct = ContentType.objects.get_for_model(self.webpath)
        self.owner = ContextUnitTest.create_user(username='owner',
                                                 is_staff=True,
                                                 is_superuser=True)
        self.user = ContextUnitTest.create_user(username='other',
                                                is_staff=True)
        self.addCleanup(cache.clear)

    def _set_owner_lock(self):
        # tests settings use LOCKS_CACHE_TTL = 0, store the lock directly
        key = f'{LOCKS_CACHE_KEY_PREFIX}{self.ct.pk}_{self.webpath.pk}'
        cache.set(key, self.owner.pk, 60)

    def test_get_lock_of_another_user(self):
        url = reverse('unicms_api:editorial-board-redis-lock',
                      kwargs={'content_type_id': self.ct.pk,
                              'object_id': self.webpath.pk})
        self.req.force_login(self.user)
        assert self.req.get(url).json() == {}
        self._set_owner_lock()
        res = self.req.get(url)
        assert str(self.owner) in res.json()['message']
        # lock owner gets no message
        self.req.force_login(self.owner)
        assert self.req.get(url).json() == {}

    def test_set_lock(self):
        url = reverse('unicms_api:editorial-board-redis-lock-set')
        data = {'content_type_id': self.ct.pk,
                'object_id': self.webpath.pk}
        self.req.force_login(self.user)
        # missing params
        res = self.req.post(url, {'content_type_id': self.ct.pk},
                            content_type='application/json')
        assert res.status_code == 404
        # user can't lock the object
        res = self.req.post(url, data, content_type='application/json')
        assert res.status_code == 403
        assert get_lock_from_cache(self.ct.pk, self.webpath.pk) == 0
        # object locked by another user
        self._set_owner_lock()
        res = self.req.post(url, data, content_type='application/json')
        assert res.status_code == 403
        assert str(self.owner) in res.json()['detail']
        assert get_lock_from_cache(self.ct.pk, self.webpath.pk) == self.owner.pk

    def test_edit_locked_object(self):
        # generic views refuse changes on objects locked by others
        carousel = CarouselUnitTest.create_carousel()
        ct = ContentType.objects.get_for_model(carousel)
        cache.set(f'{LOCKS_CACHE_KEY_PREFIX}{ct.pk}_{carousel.pk}',
                  self.owner.pk, 60)
        self.user.is_superuser = True
        self.user.save()
        self.req.force_login(self.user)
        url = reverse('unicms_api:carousel', kwargs={'pk': carousel.pk})
        res = self.req.patch(url, {'name': 'changed'},
                             content_type='application/json')
        assert res.status_code == 403
        carousel.refresh_from_db()
        assert carousel.name != 'changed'
