from rest_framework import serializers

from cms.api.serializers import UniCMSContentTypeClass, UniCMSCreateUpdateSerializer
from cms.contexts.serializers import WebPathSerializer

from . models import *


class MenuSerializer(UniCMSCreateUpdateSerializer,
                     UniCMSContentTypeClass):

    class Meta:
        model = NavigationBar
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')


class MenuForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            menu_id = self.context['request'].parser_context['kwargs']['menu_id']
            return NavigationBar.objects.filter(pk=menu_id)
        return None # pragma: no cover


class MenuItemForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            menu_id = self.context['request'].parser_context['kwargs']['menu_id']
            return NavigationBarItem.objects.filter(menu__pk=menu_id)
        return None # pragma: no cover


class MenuItemSerializer(UniCMSCreateUpdateSerializer,
                         UniCMSContentTypeClass):
    menu = MenuForeignKey()
    parent = MenuItemForeignKey(required=False, allow_null=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        webpath = WebPathSerializer(instance.webpath)
        data['webpath'] = webpath.data
        return data

    class Meta:
        model = NavigationBarItem
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')
