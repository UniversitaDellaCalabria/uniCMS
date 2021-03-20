import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.menus.models import NavigationBar
from cms.menus.tests import MenuUnitTest

from cms.contexts.tests import ContextUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MenuAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_menu(self):
        """
        Menu API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        menu = MenuUnitTest.create_menu()

        # menu list
        url = reverse('unicms_api:editorial-board-menus')

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
        data = {'name': 'posted name',
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.post(url, data=data, follow=1)
        assert NavigationBar.objects.filter(name='posted name').first()

        # GET, patch, put, delete
        url = reverse('unicms_api:editorial-board-menu', kwargs={'pk': menu.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        data = {'name': 'patched'}
        # user hasn't permission
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 403
        # user has permission
        menu.created_by = user2
        menu.save()
        content_type = ContentType.objects.get_for_model(NavigationBar)
        edit_perm = Permission.objects.get(content_type=content_type, codename='change_navigationbar')
        user2.user_permissions.add(edit_perm)
        user2.refresh_from_db()
        req.force_login(user2)
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        menu.refresh_from_db()
        assert menu.name == 'patched'

        # PUT
        menu.created_by = None
        menu.save()
        data = {'name': 'menu api-test',
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, content_type='application/json')
        menu.refresh_from_db()
        assert menu.name == 'menu api-test'
        assert not menu.is_active

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            menu.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:editorial-board-menu-form')
        res = req.get(url)
        assert isinstance(res.json(), list)
