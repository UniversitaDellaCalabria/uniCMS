import logging

from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.contexts.tests import ContextUnitTest

from cms.pages.models import PageLocalization
from cms.pages.tests import PageUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PageLocalizationAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_page_localization(self):
        """
        Page Localization API
        """
        req = Client()
        user2 = ContextUnitTest.create_user(username='staff',
                                            first_name="name",
                                            last_name="surname",
                                            email="hi@test.hi",
                                            is_staff=True)

        ebu = ContextUnitTest.create_editorialboard_user()
        user = ebu.user
        webpath = ebu.webpath
        site = webpath.site

        page = PageUnitTest.create_page()
        page.webpath = webpath
        page.save()

        # page localization list
        url = reverse('unicms_api:editorial-board-site-webpath-page-localizations',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        # site is not managed by user2
        req.force_login(user2)
        res = req.get(url)
        assert res.status_code == 403
        # user is staff
        user.is_staff = True
        user.is_superuser = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

        # POST
        data = {'page': page.pk,
                'title': 'en loc',
                'language': 'en',
                'is_active': True
                }
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1,
                       content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.post(url, data=data, follow=1,
                       content_type='application/json')
        page_loc = PageLocalization.objects.filter(page=page).last()
        assert page_loc

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-site-webpath-page-localization',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk,
                              'pk': page_loc.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        data = {'is_active': False}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has not permission on page but can manage site
        webpath2 = ContextUnitTest.create_webpath(site=site)
        ebu2 = ContextUnitTest.create_editorialboard_user(user=user2,
                                                          webpath=webpath2,
                                                          permission=6)
        ebu3 = ContextUnitTest.create_editorialboard_user(user=user2,
                                                          webpath=webpath,
                                                          permission=0)
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has permission on page
        ebu3.permission = 1
        ebu3.save()
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        page_loc.refresh_from_db()
        assert not page_loc.is_active

        # PUT
        data = {'page': page.pk,
                'title': 'new title',
                'language': 'ar',
                'is_active': False
        }
        # user hasn't permission
        ebu3.permission = 0
        ebu3.save()
        res = req.put(url, data, follow=1,
                      content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, follow=1,
                      content_type='application/json')
        page_loc.refresh_from_db()
        assert not page_loc.is_active
        assert page_loc.language == 'ar'

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            page_loc.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:editorial-board-site-webpath-page-localization-form',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)
