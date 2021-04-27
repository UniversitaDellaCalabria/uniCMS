import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.contexts.tests import ContextUnitTest


from cms.publications.models import Publication, PublicationRelated
from cms.publications.tests import PublicationUnitTest



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PublicationRelatedAPIUnitTest(TestCase):

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
        pub2 = PublicationUnitTest.create_pub()

        # pulication list
        url = reverse('unicms_api:editorial-board-publication-related-list',
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
                'related': pub2.pk,
        }
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.post(url, data=data, follow=1,
                       content_type='application/json')
        pub_related = PublicationRelated.objects.filter(publication=pub,
                                                        related=pub2).first()
        assert(pub_related)

        # GET LOGS
        url = reverse('unicms_api:editorial-board-publication-related-logs',
                      kwargs={'publication_id': pub.pk,
                              'pk': pub_related.pk})
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-publication-related',
                      kwargs={'publication_id': pub.pk,
                              'pk': pub_related.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        pub3 = PublicationUnitTest.create_pub()
        data = {'related': pub3.pk}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has permission
        pub.created_by = user2
        pub.save()
        content_type = ContentType.objects.get_for_model(Publication)
        edit_perm = Permission.objects.get(content_type=content_type, codename='change_publication')
        user2.user_permissions.add(edit_perm)
        user2.refresh_from_db()
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        pub_related.refresh_from_db()
        assert pub_related.related == pub3

        # PUT
        pub.created_by = None
        pub.save()
        data = {'publication': pub.pk,
                'related': pub2.pk,
        }
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, content_type='application/json')
        pub_related.refresh_from_db()
        assert pub_related.related == pub2

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            pub_related.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:editorial-board-publication-related-form',
                      kwargs={'publication_id': pub.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)

