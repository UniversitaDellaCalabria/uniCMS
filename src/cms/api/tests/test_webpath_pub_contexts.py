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

        url = reverse('unicms_api:editorial-board-all-publication-contexts')
        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

        user.is_staff = False
        user.save()
        url = reverse('unicms_api:editorial-board-all-publication-contexts-options')
        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)
        user.is_staff = False
        user.save()

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

        # GET LOGS
        url = reverse('unicms_api:editorial-board-site-webpath-publication-context-logs',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'pk': pub_cxt.pk})
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

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
                'in_evidence_start': '',
                'in_evidence_end': '',
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

    def _publisher_setup(self):
        user = ContextUnitTest.create_user(username='publisher',
                                           is_staff=True)
        pub = PublicationUnitTest.create_pub(count=1)
        pub_cxt = PublicationContext.objects.get(publication=pub)
        webpath = pub_cxt.webpath
        # user can publish in webpath
        EditorialBoardEditors.objects.create(webpath=webpath,
                                             user=user,
                                             permission=6,
                                             is_active=True)
        # another webpath of the same site
        new_webpath = ContextUnitTest.create_webpath(path='other-webpath')
        return user, pub, pub_cxt, webpath, new_webpath

    def test_publication_context_move_to_webpath(self):
        user, pub, pub_cxt, webpath, new_webpath = self._publisher_setup()
        site = webpath.site
        req = Client()
        req.force_login(user)
        url = reverse('unicms_api:editorial-board-site-webpath-publication-context',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'pk': pub_cxt.pk})
        patch_data = {'webpath': new_webpath.pk}
        put_data = {'publication': pub.pk,
                    'webpath': new_webpath.pk,
                    'date_start': timezone.localtime(),
                    'date_end': timezone.localtime() + timezone.timedelta(hours=1),
                    'is_active': 1}

        # user can't publish in the new webpath
        res = req.patch(url, patch_data, content_type='application/json')
        assert res.status_code == 403
        res = req.put(url, put_data, content_type='application/json')
        assert res.status_code == 403
        pub_cxt.refresh_from_db()
        assert pub_cxt.webpath == webpath

        # user can publish in the new webpath
        EditorialBoardEditors.objects.create(webpath=new_webpath,
                                             user=user,
                                             permission=6,
                                             is_active=True)
        res = req.put(url, put_data, content_type='application/json')
        assert res.status_code == 200
        pub_cxt.refresh_from_db()
        assert pub_cxt.webpath == new_webpath

        # move it back with PATCH
        url = reverse('unicms_api:editorial-board-site-webpath-publication-context',
                      kwargs={'site_id': site.pk,
                              'webpath_id': new_webpath.pk,
                              'pk': pub_cxt.pk})
        res = req.patch(url, {'webpath': webpath.pk},
                        content_type='application/json')
        assert res.status_code == 200
        pub_cxt.refresh_from_db()
        assert pub_cxt.webpath == webpath

    def test_publication_context_logs_site_not_managed(self):
        user = ContextUnitTest.create_user(username='staff-only',
                                           is_staff=True)
        pub = PublicationUnitTest.create_pub(count=1)
        pub_cxt = PublicationContext.objects.get(publication=pub)
        webpath = pub_cxt.webpath
        req = Client()
        req.force_login(user)
        url = reverse('unicms_api:editorial-board-site-webpath-publication-context-logs',
                      kwargs={'site_id': webpath.site.pk,
                              'webpath_id': webpath.pk,
                              'pk': pub_cxt.pk})
        # user doesn't manage the website
        res = req.get(url)
        assert res.status_code == 403
        # editorial board user manages the website
        EditorialBoardEditors.objects.create(webpath=webpath,
                                             user=user,
                                             permission=6,
                                             is_active=True)
        res = req.get(url)
        assert res.status_code == 200
        assert isinstance(res.json(), dict)
