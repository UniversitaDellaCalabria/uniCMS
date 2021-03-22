import logging

from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.contexts.tests import ContextUnitTest

from cms.pages.models import PageBlock
from cms.pages.tests import PageUnitTest

from cms.templates.tests import TemplateUnitTest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PageBlockAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_page_block(self):
        """
        Page Block API
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
        TemplateUnitTest.create_page_block_template()
        # page blocks list
        url = reverse('unicms_api:editorial-board-site-webpath-page-blocks',
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

        # page template blocks list
        url = reverse('unicms_api:editorial-board-template-blocks',
                      kwargs={'template_id': page.base_template.pk})
        # accessible to staff users only
        res = req.get(url)
        assert isinstance(res.json(), list)

        url = reverse('unicms_api:editorial-board-site-webpath-page-blocks',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk})
        # POST
        block = TemplateUnitTest.create_block_template()
        data = {'page': page.pk,
                'block': block.pk,
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
        page_block = PageBlock.objects.filter(block=block).last()
        assert page_block

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-site-webpath-page-block',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk,
                              'pk': page_block.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        data = {'is_active': False}
        # user hasn't permission on site
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has a poor permission
        ebu3 = ContextUnitTest.create_editorialboard_user(user=user2,
                                                          webpath=webpath,
                                                          permission=1)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has permission
        ebu3.permission = 3
        ebu3.save()
        page.created_by = user2
        page.save()
        user2.refresh_from_db()
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        page_block.refresh_from_db()
        assert not page_block.is_active

        # PUT
        page.created_by = None
        page.save()
        data = {'page': page.pk,
                'block': block.pk,
                'is_active': True
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
        page_block.refresh_from_db()
        assert page_block.is_active

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            page_block.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:editorial-board-site-webpath-page-block-form',
                      kwargs={'site_id': site.pk,
                              'webpath_id': webpath.pk,
                              'page_id': page.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)
