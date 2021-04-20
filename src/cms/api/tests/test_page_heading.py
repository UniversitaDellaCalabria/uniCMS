import logging

from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.contexts.tests import ContextUnitTest

from cms.pages.models import PageHeading, PageHeadingLocalization
from cms.pages.tests import PageUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PageHeadingAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_page_heading(self):
        """
        Page Heading API
        """
        req = Client()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)

        ebu = ContextUnitTest.create_editorialboard_user()
        user = ebu.user
        webpath = ebu.webpath
        site = webpath.site

        page = PageUnitTest.create_page()
        page.webpath = webpath
        page.save()

        # page headings list
        url = reverse('unicms_api:editorial-board-site-webpath-page-headings',
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
                'title': 'heading name',
                'description': 'heading descr',
                'is_active': 1
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
        page_heading = PageHeading.objects.filter(page=page).last()
        assert page_heading

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-site-webpath-page-heading',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk,
                              'pk': page_heading.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        data = {'title': 'patched'}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has permission on page
        page.created_by = user2
        page.save()
        ebu3 = ContextUnitTest.create_editorialboard_user(user=user2,
                                                          webpath=webpath,
                                                          permission=3)
        user2.refresh_from_db()
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        page_heading.refresh_from_db()
        assert page_heading.title == 'patched'

        # PUT
        page.created_by = None
        page.save()
        data = {'page': page.pk,
                'title': 'putted',
                'description': 'new descr',
                'is_active': 1
        }
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, follow=1,
                      content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, follow=1,
                      content_type='application/json')
        page_heading.refresh_from_db()
        assert page_heading.title == 'putted'

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            page_heading.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:editorial-board-site-webpath-page-heading-form',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)


        ###############################################################

        # page heading localizations

        # create a new heading again
        url = reverse('unicms_api:editorial-board-site-webpath-page-headings',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk})

        data = {'page': page.pk,
                'title': 'heading name',
                'description': 'heading descr',
                'is_active': 1
                }
        req.force_login(user)
        res = req.post(url, data=data, follow=1,
                       content_type='application/json')
        page_heading = PageHeading.objects.filter(page=page).last()

        # page headings list
        # page heading localizations list
        url = reverse('unicms_api:editorial-board-site-webpath-page-heading-localizations',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk,
                              'heading_id': page_heading.pk})

        # accessible to staff users only
        user.is_staff = False
        user.is_superuser = False
        user.save()
        res = req.get(url)
        assert res.status_code == 403
        # site is not managed by user2
        user3 = ContextUnitTest.create_user(username='staff 2',
                                            is_staff=True)
        req.force_login(user3)
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
        data = {'heading': page_heading.pk,
                'language': 'en',
                'title': 'heading name en',
                'description': 'heading descr en',
                'is_active': 1
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
        localization = PageHeadingLocalization.objects.filter(heading=page_heading).last()
        assert localization

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-site-webpath-page-heading-localization',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk,
                              'heading_id': page_heading.pk,
                              'pk': localization.pk})

        # GET
        # user hasn't permissions on site
        req.force_login(user3)
        res = req.get(url)
        assert res.status_code == 403
        # user has permissions
        req.force_login(user)
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        data = {'title': 'patched'}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has permission on page
        page.created_by = user2
        page.save()
        ebu3 = ContextUnitTest.create_editorialboard_user(user=user2,
                                                          webpath=webpath,
                                                          permission=3)
        user2.refresh_from_db()
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        localization.refresh_from_db()
        assert localization.title == 'patched'

        # PUT
        page.created_by = None
        page.save()
        data = {'heading': page_heading.pk,
                'language': 'fr',
                'title': 'putted',
                'description': 'new descr',
                'is_active': 1
        }
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, follow=1,
                      content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, follow=1,
                      content_type='application/json')
        localization.refresh_from_db()
        assert localization.title == 'putted'

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
        url = reverse('unicms_api:editorial-board-site-webpath-page-heading-localization-form',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk,
                              'heading_id': page_heading.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)


        # end page heading localizations

        ###############################################################
