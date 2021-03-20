import logging

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

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
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)

        webpath = ContextUnitTest.create_webpath()
        webpath_ct = ContentType.objects.get_for_model(webpath)

        # webpath locks list
        url = reverse('unicms_api:editorial-board-locks',
                      kwargs={'content_type_id': webpath_ct.pk,
                              'object_id': webpath.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.is_superuser = True
        user.save()
        req.force_login(user)
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
