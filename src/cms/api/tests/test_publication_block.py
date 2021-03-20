import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.contexts.tests import ContextUnitTest


from cms.publications.models import Publication, PublicationBlock
from cms.publications.tests import PublicationUnitTest

from cms.templates.tests import TemplateUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PublicationBlockAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_publication(self):
        """
        Publication API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        pub = PublicationUnitTest.create_pub()
        block = TemplateUnitTest.create_block_template()

        # pulication list
        url = reverse('unicms_api:editorial-board-publication-blocks',
                      kwargs={'publication_id': pub.pk})

        # accessible to staff users only
        res = req.get(url)
        assert res.status_code == 403
        user.is_staff = True
        user.is_superuser = True
        user.save()
        req.force_login(user)
        res = req.get(url)
        assert isinstance(res.json(), dict)

        # POST
        data = {'publication': pub.pk,
                'block': block.pk,
        }
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.post(url, data=data, follow=1,
                       content_type='application/json')
        pub_block = PublicationBlock.objects.filter(publication=pub,
                                                    block=block).first()
        assert(pub_block)

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-publication-block',
                      kwargs={'publication_id': pub.pk,
                              'pk': pub_block.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        block2 = TemplateUnitTest.create_block_template()
        data = {'block': block2.pk}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has permission
        pub.created_by = user2
        pub.save()
        content_type = ContentType.objects.get_for_model(Publication)
        edit_perm = Permission.objects.get(content_type=content_type, codename='change_publication')
        user2.user_permissions.add(edit_perm)
        user2.refresh_from_db()
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        pub_block.refresh_from_db()
        assert pub_block.block == block2

        # PUT
        pub.created_by = None
        pub.save()
        data = {'publication': pub.pk,
                'block': block.pk,
        }
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, content_type='application/json')
        pub_block.refresh_from_db()
        assert pub_block.block == block

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            pub_block.refresh_from_db()
        except ObjectDoesNotExist:
            assert True
