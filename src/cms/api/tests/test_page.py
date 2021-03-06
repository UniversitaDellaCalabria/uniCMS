import logging

from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from cms.contexts.tests import ContextUnitTest

from cms.pages.models import Page

from cms.templates.tests import TemplateUnitTest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PageAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_page(self):
        """
        Publication API
        """
        req = Client()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)

        ebu = ContextUnitTest.create_editorialboard_user()
        user = ebu.user
        webpath = ebu.webpath
        site = webpath.site
        template = TemplateUnitTest.create_page_template()

        # pages list
        url = reverse('unicms_api:editorial-board-site-webpath-pages',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk})

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
        data = {'name': 'test api page',
                'title': 'test api page',
                'description': 'desc',
                'webpath': webpath.pk,
                'base_template': template.pk,
                'date_start': timezone.localtime(),
                'date_end': timezone.localtime() + timezone.timedelta(hours=1),
                'tags': ["hi","tag"]
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
        page = Page.objects.filter(title='test api page').first()
        assert page

        # change status (is_active)
        url = reverse('unicms_api:editorial-board-site-webpath-page-change-status',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'pk': page.pk})
        req.force_login(user2)
        res = req.get(url, data,
                      content_type='application/json',
                      follow=1)
        assert res.status_code == 403
        # user is not a publisher
        ebu2 = ContextUnitTest.create_editorialboard_user(user=user2,
                                                          webpath=webpath,
                                                          permission=3)
        res = req.get(url, data,
                      content_type='application/json',
                      follow=1)
        assert res.status_code == 403
        # user has permission
        status = page.is_active
        req.force_login(user)
        res = req.get(url, data,
                      content_type='application/json',
                      follow=1)
        page.refresh_from_db()
        assert page.is_active != status

        # change publication status (state)
        url = reverse('unicms_api:editorial-board-site-webpath-page-change-publication-status',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'pk': page.pk})
        req.force_login(user2)
        res = req.get(url, data,
                      content_type='application/json',
                      follow=1)
        assert res.status_code == 403
        # user hasn't permission on website
        ebu2.permission = 0
        ebu2.save()
        res = req.get(url, data,
                      content_type='application/json',
                      follow=1)
        assert res.status_code == 403

        # restore user2 permission
        ebu2.permission = 3
        ebu2.save()

        # user has permission
        state = page.state
        req.force_login(user)
        res = req.get(url, data,
                      content_type='application/json',
                      follow=1)
        page.refresh_from_db()
        assert page.state != state

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-site-webpath-page',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'pk': page.pk})

        # GET
        # site is not managed by user2
        ebu2.permission = 0
        ebu2.save()
        req.force_login(user2)
        res = req.get(url, content_type='application/json')
        assert res.status_code == 403
        # site is managed by user (superuser)
        req.force_login(user)
        res = req.get(url, content_type='application/json')
        assert isinstance(res.json(), dict)

        # restore user2 permission
        ebu2.permission = 3
        ebu2.save()

        # PATCH
        data = {'title': 'patched'}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403

        # user has permission
        page.created_by = user2
        page.save()
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        page.refresh_from_db()
        assert page.title == 'patched'

        # new webpath not managed
        ebu4 = ContextUnitTest.create_editorialboard_user(user=user2,
                                                          permission=1)
        new_webpath = ebu4.webpath
        data = {'webpath': new_webpath.pk}
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403

        # PUT
        page.created_by = None
        page.save()
        data = {'name': 'test api putted',
                'title': 'test api putted',
                'description': 'desc',
                'webpath': new_webpath.pk,
                'base_template': template.pk,
                'date_start': timezone.localtime(),
                'date_end': timezone.localtime() + timezone.timedelta(hours=1),
                'tags': ["hi", "tag"],
        }
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, follow=1,
                      content_type='application/json')
        assert res.status_code == 403
        # user hasn't permission on new webpath
        page.created_by = user2
        page.save()
        res = req.put(url, data, follow=1,
                      content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, follow=1,
                      content_type='application/json')
        page.refresh_from_db()
        assert page.title == 'test api putted'

        # DELETE
        page.webpath = webpath
        page.save()
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            page.refresh_from_db()
        except ObjectDoesNotExist:
            assert True
