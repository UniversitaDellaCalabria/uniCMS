from rest_framework import serializers

from cms.api.serializers import UniCMSContentTypeClass, UniCMSCreateUpdateSerializer
from cms.contexts.serializers import WebPathSerializer
from cms.publications.serializers import PublicationSerializer

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


class MenuItemsForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            menu_id = self.context['request'].parser_context['kwargs']['menu_id']
            return NavigationBarItem.objects.filter(menu__pk=menu_id)
        return None # pragma: no cover


class MenuItemSerializer(UniCMSCreateUpdateSerializer,
                         UniCMSContentTypeClass):
    menu = MenuForeignKey()
    parent = MenuItemsForeignKey(required=False, allow_null=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        webpath = WebPathSerializer(instance.webpath)
        data['webpath'] = webpath.data
        inherited_content = PublicationSerializer(instance.inherited_content)
        data['inherited_content'] = inherited_content.data
        publication = PublicationSerializer(instance.publication)
        data['publication'] = publication.data
        return data

    class Meta:
        model = NavigationBarItem
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')


class MenuItemForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            menu_id = self.context['request'].parser_context['kwargs']['menu_id']
            menu_item_id = self.context['request'].parser_context['kwargs']['menu_item_id']
            return NavigationBarItem.objects.filter(menu__pk=menu_id,
                                                    pk=menu_item_id)
        return None # pragma: no cover


class MenuItemLocalizationSerializer(UniCMSCreateUpdateSerializer,
                                     UniCMSContentTypeClass):
    item = MenuItemForeignKey()

    class Meta:
        model = NavigationBarItemLocalization
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')


class MenuSelectOptionsSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['value'] = instance.pk
        data['text'] = instance.name
        return data

    class Meta:
        model = NavigationBar
        fields = ()
