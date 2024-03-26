from django.conf import settings
from django.utils.text import slugify

from cms.api.serializers import UniCMSCreateUpdateSerializer, UniCMSContentTypeClass

from cms.contexts import settings as contexts_settings
from cms.contexts.models import EditorialBoardEditors

from rest_framework import serializers

from . import settings as app_settings
from . models import *


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)
AUTH_USER_GROUPS = app_settings.AUTH_USER_GROUPS + getattr(settings, 'AUTH_USER_GROUPS', ())


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
                  'get_absolute_url',
                  'meta_description',
                  'meta_keywords',
                  'robots',
                  'access',
                  'is_active']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.parent:
            parent = WebPathSerializer(instance.parent)
            data['parent'] = parent.data
        if instance.alias:
            alias = WebPathSerializer(instance.alias)
            data['alias'] = alias.data
        data['full_name'] = instance.__str__()
        request = self.context.get('request', None)
        if request and request.user:
            context_permissions = dict(CMS_CONTEXT_PERMISSIONS)
            permission = EditorialBoardEditors.get_permission(instance, request.user)
            data['permission_id'] = permission
            data['permission_label'] = context_permissions[permission]
        return data

    def validate_path(self, value):
        """
        slugify path
        """
        return slugify(value)

    # def create(self, validated_data):
        # try:
        # return WebPath.objects.create(**validated_data)
        # except Exception as e:
        # raise e

    # def update(self, instance, validated_data):
        # try:
        # return super().update(instance, validated_data)
        # except Exception as e:
        # raise e


class WebPathSelectOptionsSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['value'] = instance.pk
        data['text'] = instance.__str__()
        return data

    class Meta:
        model = WebPath
        fields = ()
