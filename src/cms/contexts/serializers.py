from rest_framework import serializers

from . models import EditorialBoardEditors, WebPath, WebSite


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


class WebPathSerializer(serializers.ModelSerializer):

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
