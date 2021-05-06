from django.forms import ModelForm
from django.urls import reverse

from cms.api.settings import FORM_SOURCE_LABEL

from . models import NavigationBar, NavigationBarItem, NavigationBarItemLocalization


class MenuForm(ModelForm):

    class Meta:
        model = NavigationBar
        fields = ['name', 'is_active']


class MenuItemForm(ModelForm):

    def __init__(self, *args, **kwargs):
        menu_id = kwargs.pop('menu_id', None)
        super().__init__(*args, **kwargs)
        if menu_id:
            self.fields['menu'].queryset = NavigationBar.objects.filter(pk=menu_id)
            self.fields['parent'].queryset = NavigationBarItem.objects.filter(menu__pk=menu_id)
        setattr(self.fields['webpath'],
                FORM_SOURCE_LABEL,
                reverse('unicms_api:webpath-all-options'))
        setattr(self.fields['publication'],
                FORM_SOURCE_LABEL,
                reverse('unicms_api:editorial-board-publications-options'))
        setattr(self.fields['inherited_content'],
                FORM_SOURCE_LABEL,
                reverse('unicms_api:editorial-board-publications-options'))

    class Meta:
        model = NavigationBarItem
        fields = ['menu', 'name', 'webpath', 'parent', 'url',
                  'publication',
                  'inherited_content',
                  'order', 'is_active']


class MenuItemLocalizationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        menu_id = kwargs.pop('menu_id', None)
        menu_item_id = kwargs.pop('menu_item_id', None)
        super().__init__(*args, **kwargs)
        if menu_id and menu_item_id:
            self.fields['item'].queryset = NavigationBarItem.objects.filter(pk=menu_item_id,
                                                                                 menu__pk=menu_id)

    class Meta:
        model = NavigationBarItemLocalization
        fields = ['item', 'language', 'name', 'is_active']
