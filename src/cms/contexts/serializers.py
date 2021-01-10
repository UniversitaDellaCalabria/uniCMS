from rest_framework import serializers

from . models import WebPath


class WebPathSerializer(serializers.ModelSerializer):
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
