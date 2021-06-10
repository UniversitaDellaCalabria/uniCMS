import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.menus.models import NavigationBar, NavigationBarItem
from cms.menus.tests import MenuUnitTest

from cms.contexts.tests import ContextUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MenuItemAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_menu_item(self):
        """
        Menu Item API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        menu_item = MenuUnitTest.create_menu_item()
        menu = menu_item.menu

        data_item = {'menu': menu,
                     'name': 'Didattica',
                     'url': 'http://example.org',
                     # 'publication_id': None,
                     # 'webpath_id': None,
                     'is_active': True}
        menu_item2 = MenuUnitTest.create_menu_item(**data_item)
        menu_item2.parent = menu_item
        menu_item2.save()

        menu_item3 = MenuUnitTest.create_menu_item(**data_item)
        menu_item3.parent = menu_item2
        menu_item3.save()

        # menu items list
        url = reverse('unicms_api:editorial-board-menu-items',
                      kwargs={'menu_id': menu.pk})

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
        data = {'menu': menu.pk,
                'name': 'posted',
                'url': 'http://test.test',
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        # wrong parent menu
        data['menu'] = 11121
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 400
        # wrong parent menu
        menu_2 = MenuUnitTest.create_menu()
        data['menu'] = menu_2.pk
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 400
        # correct data
        data['menu'] = menu.pk
        res = req.post(url, data=data, follow=1)
        assert NavigationBarItem.objects.filter(name='posted').first()

        # GET LOGS
        url = reverse('unicms_api:editorial-board-menu-item-logs',
                      kwargs={'menu_id': menu.pk,
                              'pk': menu_item.pk})
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # redis lock set
        ct = ContentType.objects.get_for_model(menu_item)
        url = reverse('unicms_api:editorial-board-redis-lock-set')
        data = {'content_type_id': ct.pk,
                'object_id': menu_item.pk}
        res = req.post(url, data,
                       content_type='application/json', follow=1)
        assert isinstance(res.json(), dict)

        # GET, patch, put, delete

        # GET
        url = reverse('unicms_api:editorial-board-menu-item',
                      kwargs={'menu_id': menu.pk,
                              'pk': menu_item.pk})

        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH

        # set child as parent (not permitted)
        data = {'parent': menu_item3.pk}
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 400

        # wrong menu id
        data = {'menu': 1221321312}
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 400
        # patch menu id
        data = {'menu': menu_item.menu.pk}
        res = req.patch(url, data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 200
        # correct data
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
        menu_item.refresh_from_db()
        assert menu_item.name == 'patched'

        # PUT
        menu.created_by = None
        menu.save()
        data = {'menu': menu_item.menu.pk,
                'name': 'putted',
                'parent': '',
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data,
                      content_type='application/json',
                      follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data,
                      content_type='application/json',
                      follow=1)
        menu_item.refresh_from_db()
        assert menu_item.name == 'putted'
        assert not menu_item.is_active

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            menu_item.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # menu item form
        url = reverse('unicms_api:editorial-board-menu-item-form',
                      kwargs={'menu_id': menu.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)
