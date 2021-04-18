from django.forms import ModelForm
from django.urls import reverse

from cms.api.settings import FORM_SOURCE_LABEL

from . models import NavigationBar, NavigationBarItem


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

    class Meta:
        model = NavigationBarItem
        fields = ['menu', 'name', 'webpath', 'parent', 'url',
                  #'publication', 'inherited_content',
                  'order', 'is_active']
