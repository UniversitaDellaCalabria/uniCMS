import logging

from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from cms.contexts.models import EditorialBoardEditors
from cms.contexts.tests import ContextUnitTest

from cms.publications.models import PublicationContext
from cms.publications.tests import PublicationUnitTest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class WebpathPubContextAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_publication_context(self):
        """
        Carousel API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        pub = PublicationUnitTest.create_pub()
        pub_cxt = PublicationContext.objects.get(publication=pub)
        webpath = pub_cxt.webpath
        site = webpath.site
        # webpath pubs list

        url = reverse('unicms_api:editorial-board-site-webpath-publication-contexts',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.save()
        req.force_login(user)
        # user must manage website
        res = req.get(url)
        assert res.status_code == 403
        # user is editor but no publisher
        editor_perm = EditorialBoardEditors.objects.create(webpath=webpath,
                                                           user=user,
                                                           permission=5,
                                                           is_active=True)
        # superuser can do (user is only an editor)
        res = req.get(url)
        assert isinstance(res.json(), dict)

        # POST
        pub2 = PublicationUnitTest.create_pub()
        data = {'publication': pub2.pk,
                'webpath': webpath.pk,
                'date_start': timezone.localtime(),
                'date_end': timezone.localtime() + timezone.timedelta(hours=1),
        }
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        user.is_superuser = True
        user.save()
        req.force_login(user)
        res = req.post(url, data=data, follow=1,
                       content_type='application/json')
        pub_cxt = PublicationContext.objects.filter(publication=pub2,
                                                    webpath=webpath).first()
        assert pub_cxt

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-site-webpath-publication-context',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'pk': pub_cxt.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        data = {'in_evidence_start': pub_cxt.date_start,
                'is_active': 1}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        # user hasn't access to website
        assert res.status_code == 403
        # user is only an editor
        user.is_superuser = False
        user.save()
        req.force_login(user)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user is superuser
        user.is_superuser = True
        user.save()
        req.force_login(user)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        pub_cxt.refresh_from_db()
        assert pub_cxt.in_evidence_start == pub_cxt.date_start
        assert pub_cxt.is_active

        # PUT
        pub_cxt.created_by = None
        pub_cxt.save()
        data = {'publication': pub.pk,
                'webpath': webpath.pk,
                'date_start': timezone.localtime(),
                'date_end': timezone.localtime() + timezone.timedelta(hours=1),
                'is_active': 0,
        }
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, content_type='application/json')
        assert res.status_code == 403
        # user is only an editor
        user.is_superuser = False
        user.save()
        req.force_login(user)
        res = req.put(url, data,
                      content_type='application/json',
                      follow=1)
        assert res.status_code == 403
        # user is superuser
        user.is_superuser = True
        user.save()
        req.force_login(user)
        res = req.put(url, data, content_type='application/json')
        pub_cxt.refresh_from_db()
        assert pub_cxt.publication == pub
        assert not pub_cxt.is_active
        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user is only an editor
        user.is_superuser = False
        user.save()
        req.force_login(user)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        user.is_superuser = True
        user.save()
        req.force_login(user)
        res = req.delete(url)
        try:
            pub_cxt.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:editorial-board-site-webpath-publication-context-form',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)

        url = reverse('unicms_api:editorial-board-site-webpath-publication-context-form-generic',
                      kwargs={'site_id': site.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)

        url = reverse('unicms_api:users-form')
        res = req.get(url)
        assert isinstance(res.json(), list)
