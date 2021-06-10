import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.menus.models import NavigationBar, NavigationBarItemLocalization
from cms.menus.tests import MenuUnitTest

from cms.contexts.tests import ContextUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MenuItemLocalizationAPIUnitTest(TestCase):

    def setUp(self):
        pass

    def test_menu_item_localization(self):
        """
        Menu Item Localization API
        """
        req = Client()
        user = ContextUnitTest.create_user()
        user2 = ContextUnitTest.create_user(username='staff',
                                            is_staff=True)
        menu_item = MenuUnitTest.create_menu_item()
        menu = menu_item.menu

        # menu item localization list
        url = reverse('unicms_api:menu-item-localizations',
                      kwargs={'menu_id': menu.pk,
                              'menu_item_id': menu_item.pk})

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
        data = {'item': menu_item.pk,
                'language': 'en',
                'name': 'english',
                'is_active': 0}

        # user hasn't permission
        req.force_login(user2)
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        # wrong carousel item
        menu_item_2 = MenuUnitTest.create_menu_item(menu=menu)
        data['item'] = menu_item_2.pk
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 400
        # wrong carousel_item
        data['item'] = 11121
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 400
        data['item'] = menu_item.pk
        # wrong parent menu
        url = reverse('unicms_api:menu-item-localizations',
                      kwargs={'menu_id': 12321321,
                              'menu_item_id': menu_item.pk})
        res = req.post(url, data=data, follow=1)
        assert res.status_code == 400
        url = reverse('unicms_api:menu-item-localizations',
                      kwargs={'menu_id': menu.pk,
                              'menu_item_id': menu_item.pk})
        res = req.post(url, data=data, follow=1)
        localization = NavigationBarItemLocalization.objects.filter(name='english').first()
        assert localization

        # GET LOGS
        url = reverse('unicms_api:menu-item-localization-logs',
                      kwargs={'menu_id': menu.pk,
                              'menu_item_id': menu_item.pk,
                              'pk': localization.pk})
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # redis lock set
        ct = ContentType.objects.get_for_model(localization)
        url = reverse('unicms_api:editorial-board-redis-lock-set')
        data = {'content_type_id': ct.pk,
                'object_id': localization.pk}
        res = req.post(url, data,
                       content_type='application/json', follow=1)
        assert isinstance(res.json(), dict)

        # GET, patch, put, delete
        url = reverse('unicms_api:menu-item-localization',
                      kwargs={'menu_id': menu.pk,
                              'menu_item_id': menu_item.pk,
                              'pk': localization.pk})

        # GET
        res = req.get(url, content_type='application/json',)
        assert isinstance(res.json(), dict)

        # PATCH
        # wrong parent menu item
        data = {'item': 11121}
        res = req.patch(url, data=data,
                        content_type='application/json',
                        follow=1)
        assert res.status_code == 400
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
        localization.refresh_from_db()
        assert localization.name == 'patched'

        # PUT
        menu.created_by = None
        menu.save()
        data = {'item': menu_item.pk,
                'language': 'en',
                'name': 'putted',
                'is_active': 0}
        # user hasn't permission
        req.force_login(user2)
        res = req.put(url, data, content_type='application/json')
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.put(url, data, content_type='application/json')
        localization.refresh_from_db()
        assert localization.name == 'putted'
        assert not localization.is_active

        # DELETE
        # user hasn't permission
        req.force_login(user2)
        res = req.delete(url)
        assert res.status_code == 403
        # user has permission
        req.force_login(user)
        res = req.delete(url)
        try:
            localization.refresh_from_db()
        except ObjectDoesNotExist:
            assert True

        # form
        url = reverse('unicms_api:menu-item-localization-form',
                      kwargs={'menu_id': menu.pk,
                              'menu_item_id': menu_item.pk})
        res = req.get(url)
        assert isinstance(res.json(), list)
