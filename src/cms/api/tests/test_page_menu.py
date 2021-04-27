import logging

from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.contexts.tests import ContextUnitTest

from cms.menus.tests import MenuUnitTest

from cms.pages.models import PageMenu
from cms.pages.tests import PageUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PageMenuAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_page_menu(self):
        """
        Page Menu API
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

        # page links list
        url = reverse('unicms_api:editorial-board-site-webpath-page-menus',
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
        menu = MenuUnitTest.create_menu()
        data = {'page': page.pk,
                'menu': menu.pk,
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
        page_menu = PageMenu.objects.filter(page=page).last()
        assert page_menu

        # GET LOGS
        url = reverse('unicms_api:editorial-board-site-webpath-page-menu-logs',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk,
                              'pk': page_menu.pk})
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-site-webpath-page-menu',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk,
                              'pk': page_menu.pk})

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
        page_menu.refresh_from_db()
        assert not page_menu.is_active

        # PUT
        page.created_by = None
        page.save()
        data = {'page': page.pk,
                'menu': menu.pk,
                'is_active': False
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
        page_menu.refresh_from_db()
        assert not page_menu.is_active

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            page_menu.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:editorial-board-site-webpath-page-menu-form',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)
