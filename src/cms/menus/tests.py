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
        
        menu_item.link
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
        
    
    
    
