import logging

from django.test import Client, TestCase
from django.urls import reverse


from cms.contexts.tests import ContextUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class WebsiteAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_website(self):
        """
        Website API
        """
        req = Client()
        user = ContextUnitTest.create_user(username='user-1')
        webpath = ContextUnitTest.create_webpath()
        # two editorialboard_user with different webpaths
        ContextUnitTest.create_editorialboard_user(user=user,
                                                   webpath=webpath,
                                                   permission=1,
                                                   is_active=True)
        ContextUnitTest.create_editorialboard_user(user=user,
                                                   webpath=None,
                                                   permission=8,
                                                   is_active=True)
        url = reverse('unicms_api:editorial-board-sites')
        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

        url = reverse('unicms_api:editorial-board-site',
                      kwargs={'pk': webpath.site.pk})
        # accessible to staff users only
        res = req.get(url)
        assert isinstance(res.json(), dict)
