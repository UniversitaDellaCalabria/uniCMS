import logging

from django.test import Client, TestCase
from django.urls import reverse

from cms.templates.tests import TemplateUnitTest

from cms.contexts.tests import ContextUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TemplateBlockAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_template_block(self):
        """
        Template Block API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        template_block = TemplateUnitTest.create_page_block_template()
        template = template_block.template

        # template blocks list
        url = reverse('unicms_api:editorial-board-template-block',
                      kwargs={'template_id': template.pk,
                              'pk': template_block.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.is_superuser = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

