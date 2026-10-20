import logging

from django.test import TestCase

from . models import NavigationBar, NavigationBarItem, NavigationBarItemLocalization


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MenuUnitTest(TestCase):

    def setUp(self):
        pass

    @classmethod
    def create_menu(cls, **kwargs):
        if not kwargs:
            kwargs =  {'name': 'main menu',
                       'is_active': 1}
        obj = NavigationBar.objects.create(**kwargs)
        return obj


    @classmethod
    def create_menu_item(cls, **kwargs):
        menu = cls.create_menu()
        data = {'menu': menu,
                # 'parent_id': None,
                'name': 'Didattica',
                'url': 'http://example.org',
                # 'publication_id': None,
                # 'webpath_id': None,
                'is_active': True}
        for k,v in kwargs.items():
            data[k] = v
        obj = NavigationBarItem.objects.create(**data)
        return obj


    @classmethod
    def test_menu(cls):
        menu = cls.create_menu()

        menu.__str__()

        menu.get_items(lang='en')
        menu.serialize(lang='en')

        # TODO - import json menu items
        list_of_dict = [{}]
        menu.import_childs(list_of_dict)


    @classmethod
    def test_menu_item(cls):
        menu_item = cls.create_menu_item()
        menu_item.__str__()

        menu_item.link()
        menu_item.localized(lang='en')
        menu_item.serialize(lang='en')
        menu_item.get_childs(lang='en')

        menu_item.has_childs()
        menu_item.childs_count()
        menu_item.get_siblings_count()

        menu_loc = NavigationBarItemLocalization.objects.create(
                        item = menu_item,
                        language = 'en',
                        name = 'menu item eng'
        )
        menu_loc.__str__()






# --- tree serialization, import, localization, serializers, forms, template tags ---

from types import SimpleNamespace
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import RequestFactory, override_settings
from django.utils.safestring import SafeString

from cms.contexts.tests import ContextUnitTest

from . forms import MenuItemForm, MenuItemLocalizationForm
from . serializers import (MenuForeignKey,
                           MenuItemForeignKey,
                           MenuItemLocalizationSerializer,
                           MenuItemsForeignKey,
                           MenuItemSerializer,
                           MenuSelectOptionsSerializer)
from . templatetags.unicms_menus import (load_item_childs,
                                         load_item_inherited_content,
                                         load_item_publication,
                                         load_menu)


MENU_TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {
        'loaders': [('django.template.loaders.locmem.Loader', {
            'menu.html': '{% for i in items %}[{{ i.name }}]{% endfor %}',
            'broken.html': '{% for %}',
        })],
    },
}]


class MenuTreeUnitTest(TestCase):

    def setUp(self):
        self.menu = NavigationBar.objects.create(name='menu', is_active=True)
        self.webpath = ContextUnitTest.create_webpath(path='menu-path')
        self.root = NavigationBarItem.objects.create(menu=self.menu, name='root',
                                                     url='https://example.org',
                                                     order=1, is_active=True)
        self.child = NavigationBarItem.objects.create(menu=self.menu, name='child',
                                                      parent=self.root,
                                                      webpath=self.webpath,
                                                      order=1, is_active=True)
        self.inactive = NavigationBarItem.objects.create(menu=self.menu, name='inactive',
                                                         parent=self.root,
                                                         order=2, is_active=False)
        self.grandchild = NavigationBarItem.objects.create(menu=self.menu, name='grandchild',
                                                           parent=self.child,
                                                           is_active=True)

    def test_link(self):
        self.assertEqual(self.root.link(), 'https://example.org')
        self.assertEqual(self.child.link(), self.webpath.get_site_path())
        self.assertEqual(self.grandchild.link(), '')

    def test_serialize(self):
        data = self.menu.serialize()
        self.assertEqual(data['name'], 'menu')
        self.assertTrue(data['is_active'])
        self.assertEqual(len(data['childs']), 1)
        root = data['childs'][0]
        self.assertEqual(root['name'], 'root')
        self.assertIsNone(root['parent_id'])
        self.assertEqual(root['level'], 0)
        # inactive child is excluded
        self.assertEqual([c['name'] for c in root['childs']], ['child'])
        child = root['childs'][0]
        self.assertEqual(child['parent_id'], self.root.pk)
        self.assertEqual(child['parent_name'], 'root')
        self.assertEqual(child['webpath_id'], self.webpath.pk)
        self.assertEqual(child['link'], self.webpath.get_site_path())
        self.assertEqual(child['level'], 1)
        self.assertEqual(child['childs'][0]['name'], 'grandchild')
        self.assertEqual(child['childs'][0]['level'], 2)

        # not deep
        self.assertNotIn('childs', self.root.serialize())

    def test_serialize_all(self):
        self.root.is_active = False
        self.root.save()
        self.assertEqual(self.menu.serialize()['childs'], [])
        data = self.menu.serialize(only_active=False)
        self.assertEqual(len(data['childs']), 1)
        names = [c['name'] for c in data['childs'][0]['childs']]
        self.assertEqual(names, ['child', 'inactive'])

    def test_localization(self):
        NavigationBarItemLocalization.objects.create(item=self.root, language='it',
                                                     name='radice', url='',
                                                     is_active=True)
        NavigationBarItemLocalization.objects.create(item=self.child, language='it',
                                                     name='figlio',
                                                     url='https://example.org/it',
                                                     is_active=True)
        item = NavigationBarItem.objects.get(pk=self.root.pk).localized(lang='it')
        self.assertEqual(item.name, 'radice')
        # empty localized url: original url is kept
        self.assertEqual(item.url, 'https://example.org')
        self.assertEqual(item.language, 'it')
        # no localization
        item = NavigationBarItem.objects.get(pk=self.root.pk).localized(lang='fr')
        self.assertEqual(item.name, 'root')
        self.assertIsNone(item.language)

        # items list
        self.assertEqual([i.name for i in self.menu.get_items(lang='it', parent__isnull=True)],
                         ['radice'])
        # childs are localized
        childs = self.root.get_childs(lang='it')
        self.assertEqual([c.name for c in childs], ['figlio'])
        self.assertEqual(childs[0].url, 'https://example.org/it')
        # serialized tree: first level childs are localized
        data = self.menu.serialize(lang='it')
        self.assertEqual(data['childs'][0]['childs'][0]['name'], 'figlio')

    def test_childs(self):
        self.assertEqual(list(self.root.get_childs()), [self.child])
        self.assertEqual(list(self.root.get_childs(only_active=False)),
                         [self.child, self.inactive])
        self.assertEqual(list(self.root.get_childs(only_active=False,
                                                   exclude=self.child)),
                         [self.inactive])
        # unsaved item
        self.assertIsNone(NavigationBarItem(menu=self.menu, name='new').get_childs())

        self.assertTrue(self.root.has_childs())
        self.assertFalse(self.grandchild.has_childs())
        self.assertEqual(self.root.childs_count(), 1)
        self.assertEqual(self.child.get_siblings_count(), 1)
        self.assertEqual(self.root.get_menu(), self.menu)
        self.assertEqual(self.menu.get_menu(), self.menu)
        self.assertEqual(str(self.child), 'menu: child (root)')
        self.assertEqual(str(self.root), 'menu: root ()')

    def test_item_in_childs(self):
        self.assertFalse(self.root.item_in_childs(None))
        self.assertTrue(self.root.item_in_childs(self.child))
        # inactive childs are included
        self.assertTrue(self.root.item_in_childs(self.inactive))
        # nested child
        self.assertTrue(self.root.item_in_childs(self.grandchild))
        self.assertFalse(self.child.item_in_childs(self.root))
        # leaf
        self.assertFalse(self.grandchild.item_in_childs(self.root))

    def test_parent_loop(self):
        # self as parent
        self.root.parent = self.root
        with self.assertRaises(Exception):
            self.root.save()
        # a child as parent
        root = NavigationBarItem.objects.get(pk=self.root.pk)
        root.parent = self.grandchild
        with self.assertRaises(Exception):
            root.save()
        self.assertIsNone(NavigationBarItem.objects.get(pk=self.root.pk).parent)

    def test_import_childs(self):
        menu = NavigationBar.objects.create(name='imported', is_active=True)
        tree = self.menu.serialize(only_active=False)['childs']

        # 'id' is not removed by import_childs: drop it, as in an export
        def drop_ids(items):
            for item in items:
                item.pop('id')
                drop_ids(item.get('childs', []))
        drop_ids(tree)
        self.assertTrue(menu.import_childs(tree + [{}]))
        data = menu.serialize(only_active=False)
        self.assertEqual(len(data['childs']), 1)
        root = data['childs'][0]
        self.assertEqual(root['name'], 'root')
        self.assertNotEqual(root['id'], self.root.pk)
        child = root['childs'][0]
        self.assertEqual(child['name'], 'child')
        self.assertEqual(child['webpath_id'], self.webpath.pk)
        self.assertEqual(child['childs'][0]['name'], 'grandchild')
        self.assertEqual(NavigationBarItem.objects.filter(menu=menu).count(), 4)
        # source menu is unchanged
        self.assertEqual(NavigationBarItem.objects.filter(menu=self.menu).count(), 4)

    def test_is_lockable_by(self):
        superuser = get_user_model().objects.create(username='su', is_superuser=True)
        user = get_user_model().objects.create(username='nobody')
        loc = NavigationBarItemLocalization.objects.create(item=self.root, language='it',
                                                           name='radice')
        self.assertTrue(self.root.is_lockable_by(superuser))
        self.assertFalse(self.root.is_lockable_by(user))
        self.assertTrue(loc.is_lockable_by(superuser))
        self.assertFalse(loc.is_lockable_by(user))
        self.assertEqual(str(loc), f'{self.root} - it')


class MenuSerializersUnitTest(TestCase):

    def setUp(self):
        self.menu = NavigationBar.objects.create(name='menu', is_active=True)
        self.other_menu = NavigationBar.objects.create(name='other', is_active=True)
        self.item = NavigationBarItem.objects.create(menu=self.menu, name='item')
        self.other_item = NavigationBarItem.objects.create(menu=self.other_menu,
                                                           name='other item')

    def _bind(self, field_class, serializer_class, request=None):
        field = field_class()
        context = {'request': request} if request else {}
        field.bind('field', serializer_class(context=context))
        return field

    def test_foreign_keys(self):
        request = SimpleNamespace(parser_context={'kwargs': {'menu_id': self.menu.pk,
                                                             'menu_item_id': self.item.pk}})
        for field_class, serializer_class, expected in (
                (MenuForeignKey, MenuItemSerializer, [self.menu]),
                (MenuItemsForeignKey, MenuItemSerializer, [self.item]),
                (MenuItemForeignKey, MenuItemLocalizationSerializer, [self.item])):
            self.assertIsNone(self._bind(field_class, serializer_class).get_queryset())
            field = self._bind(field_class, serializer_class, request)
            self.assertEqual(list(field.get_queryset()), expected)

    def test_menu_item_serializer(self):
        data = MenuItemSerializer(self.item).data
        self.assertEqual(data['name'], 'item')
        self.assertIsNone(data['webpath'])
        self.assertIsNone(data['publication'])
        self.assertIsNone(data['inherited_content'])

        webpath = ContextUnitTest.create_webpath(path='ser')
        self.item.webpath = webpath
        self.item.save()
        data = MenuItemSerializer(self.item).data
        self.assertEqual(data['webpath']['id'], webpath.pk)

    def test_menu_item_serializer_publications(self):
        from cms.publications.tests import PublicationUnitTest
        pub = PublicationUnitTest.create_pub(count=1)
        self.item.publication = pub
        self.item.inherited_content = pub
        self.item.save()
        data = MenuItemSerializer(self.item).data
        self.assertEqual(data['publication']['id'], pub.pk)
        self.assertEqual(data['inherited_content']['id'], pub.pk)

    def test_select_options(self):
        self.assertEqual(MenuSelectOptionsSerializer(self.menu).data,
                         {'value': self.menu.pk, 'text': 'menu'})

    def test_forms(self):
        form = MenuItemForm(menu_id=self.menu.pk)
        self.assertEqual(list(form.fields['menu'].queryset), [self.menu])
        self.assertEqual(list(form.fields['parent'].queryset), [self.item])
        form = MenuItemForm()
        self.assertEqual(form.fields['menu'].queryset.count(), 2)

        form = MenuItemLocalizationForm(menu_id=self.menu.pk,
                                        menu_item_id=self.item.pk)
        self.assertEqual(list(form.fields['item'].queryset), [self.item])
        form = MenuItemLocalizationForm(menu_id=self.menu.pk)
        self.assertEqual(form.fields['item'].queryset.count(), 2)


@override_settings(TEMPLATES=MENU_TEMPLATES)
class MenuTemplateTagsUnitTest(TestCase):

    def setUp(self):
        self.menu = NavigationBar.objects.create(name='menu', is_active=True)
        self.root = NavigationBarItem.objects.create(menu=self.menu, name='root',
                                                     order=1, is_active=True)
        self.child = NavigationBarItem.objects.create(menu=self.menu, name='child',
                                                      parent=self.root, is_active=True)
        NavigationBarItemLocalization.objects.create(item=self.root, language='it',
                                                     name='radice', is_active=True)
        self.request = RequestFactory().get('/')
        self.request.LANGUAGE_CODE = 'it'

    def _page(self, page_menus):
        page = mock.MagicMock()
        page.get_menus.return_value.filter.return_value.first.return_value = page_menus
        return page

    def test_load_menu_by_id(self):
        context = {'request': self.request}
        self.assertEqual(load_menu(context, 'menu.html', menu_id=self.menu.pk), '[radice]')
        # broken template
        self.assertIn('Error', load_menu(context, 'broken.html', menu_id=self.menu.pk))
        # missing menu
        with self.assertLogs('cms.menus.templatetags.unicms_menus', level='ERROR'):
            self.assertEqual(load_menu(context, 'menu.html', menu_id=9999), SafeString(''))

    def test_load_menu_by_section(self):
        page_menu = SimpleNamespace(menu=self.menu)
        page = self._page(page_menu)
        context = {'request': self.request, 'page': page}
        self.assertEqual(load_menu(context, 'menu.html', section='top'), '[radice]')
        page.get_menus.return_value.filter.assert_called_with(section='top')
        # no section
        self.assertEqual(load_menu(context, 'menu.html'), '')
        # no menu in section
        context['page'] = self._page(None)
        with self.assertLogs('cms.menus.templatetags.unicms_menus', level='ERROR'):
            self.assertEqual(load_menu(context, 'menu.html', section='top'), '')

    def test_load_item_childs(self):
        context = {'request': self.request}
        self.assertEqual(list(load_item_childs(context, self.root)), [self.child])
        self.assertEqual(list(load_item_childs(context, self.root, exclude=self.child)), [])
        self.assertIsNone(load_item_childs(context, None))

    def test_load_item_publications(self):
        context = {'request': self.request}
        pub = mock.MagicMock(is_active=True)
        item = SimpleNamespace(inherited_content=pub, publication=pub)
        self.assertEqual(load_item_inherited_content(context, item), pub)
        self.assertEqual(load_item_publication(context, item), pub)
        pub.translate_as.assert_called_with(lang='it')
        # inactive publication
        pub.is_active = False
        self.assertIsNone(load_item_inherited_content(context, item))
        self.assertIsNone(load_item_publication(context, item))
        # no item
        self.assertIsNone(load_item_inherited_content(context, None))
        self.assertIsNone(load_item_publication(context, None))
