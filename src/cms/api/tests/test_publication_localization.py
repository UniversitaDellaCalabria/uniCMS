import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.contexts.tests import ContextUnitTest


from cms.publications.models import EditorialBoardLock, EditorialBoardLockUser, Publication, PublicationLocalization
from cms.publications.tests import PublicationUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PublicationLocalizationAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_publication(self):
        """
        Publication API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        pub = PublicationUnitTest.create_pub()

        # pulication list
        url = reverse('unicms_api:editorial-board-publication-localizations',
                      kwargs={'publication_id': pub.pk})

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
        data = {'publication': pub.pk,
                'title': 'test en',
                'subheading': 'test en',
                'content': 'test en',
                'language': 'en',
        }
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.post(url, data=data, follow=1,
                       content_type='application/json')
        localization = PublicationLocalization.objects.filter(title='test en').first()
        assert(localization)

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-publication-localization',
                      kwargs={'publication_id': pub.pk,
                              'pk': localization.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        data = {'title': 'test en patched'}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has permission
        content_type = ContentType.objects.get_for_model(Publication)
        lock_on_pub = EditorialBoardLock.objects.create(content_type=content_type,
                                                        object_id=pub.pk)
        user_lock = EditorialBoardLockUser.objects.create(lock=lock_on_pub,
                                                          user=user)
        user2_lock = EditorialBoardLockUser.objects.create(lock=lock_on_pub,
                                                           user=user2)
        # user has a lock but he hasn't django permissions
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # with permissions
        edit_perm = Permission.objects.get(content_type=content_type,
                                           codename='change_publication')
        user2.user_permissions.add(edit_perm)
        user2.refresh_from_db()
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        localization.refresh_from_db()
        assert localization.title == 'test en patched'

        # PUT
        # pub.created_by = None
        # pub.save()
        data = {'publication': pub.pk,
                'title': 'test en putted',
                'subheading': 'test en',
                'content': 'test en',
                'language': 'en',
        }
        # user hasn't permission
        # delete lock
        user2_lock.delete()
        req.force_login(user2)
        res = req.put(url, data, content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, content_type='application/json')
        localization.refresh_from_db()
        assert localization.title == 'test en putted'

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            localization.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:editorial-board-publication-localization-form',
                      kwargs={'publication_id': pub.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)

