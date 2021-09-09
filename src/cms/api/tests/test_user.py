import logging

from django.test import Client, TestCase
from django.urls import reverse

from cms.contexts.tests import ContextUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class UserAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_user(self):
        """
        Current User API
        """
        req = Client()
        user = ContextUnitTest.create_user()

        url = reverse('unicms_api:users-current')

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), list)

    def test_user_detail(self):
        """
        User Detail API
        """
        req = Client()
        user = ContextUnitTest.create_user()

        url = reverse('unicms_api:user-detail',
                      kwargs={'user_id': user.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), object)
