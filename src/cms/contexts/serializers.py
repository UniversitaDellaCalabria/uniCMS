from django.conf import settings

from cms.api.serializers import UniCMSCreateUpdateSerializer, UniCMSContentTypeClass

from cms.contexts import settings as contexts_settings
from cms.contexts.models import EditorialBoardEditors

from rest_framework import serializers

from . models import *


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)


class EditorialBoardLockSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorialBoardLock
        fields = '__all__'


class EditorialBoardLockUserSerializer(serializers.ModelSerializer):

    lock = EditorialBoardLockSerializer()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = instance.user.__str__()
        return data

    class Meta:
        model = EditorialBoardLockUser
        fields = '__all__'


class WebSiteForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            site_id = self.context['request'].parser_context['kwargs']['site_id']
            return WebSite.objects.filter(pk=site_id)
        return None # pragma: no cover


class ParentForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            site_id = self.context['request'].parser_context['kwargs']['site_id']
            return WebPath.objects.filter(site=site_id)
        return None # pragma: no cover


class WebPathSerializer(UniCMSCreateUpdateSerializer, UniCMSContentTypeClass):

    site = WebSiteForeignKey()
    parent = ParentForeignKey()

    class Meta:
        model = WebPath
        fields = ['id',
                  'site',
                  'name',
                  'parent',
                  'get_parent_fullpath',
                  'alias',
                  'alias_url',
                  'path',
                  'get_full_path',
                  'is_active']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request', None)
        if request and request.user:
            context_permissions = dict(CMS_CONTEXT_PERMISSIONS)
            permission = EditorialBoardEditors.get_permission(instance, request.user)
            data['permission_id'] = permission
            data['permission_label'] = context_permissions[permission]
        return data
