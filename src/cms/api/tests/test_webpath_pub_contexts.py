import logging

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

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
        user.is_superuser = True
        user.save()
        req.force_login(user)
        res = req.get(url, {'is_active': True})
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
        req.force_login(user)
        res = req.post(url, data=data, follow=1,
                       content_type='application/json')
        pub_cxt = PublicationContext.objects.filter(publication=pub2,
                                                    webpath=webpath).first()
        assert pub_cxt
