from cms.contexts.models import WebPath

from rest_framework import serializers
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)

from . models import *


class PageForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            page_id = self.context['request'].parser_context['kwargs']['page_id']
            return Page.objects.filter(pk=page_id)
        return None # pragma: nocover


class WebPathForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            site_id = self.context['request'].parser_context['kwargs']['site_id']
            webpath_id = self.context['request'].parser_context['kwargs']['webpath_id']
            return WebPath.objects.filter(pk=webpath_id,
                                          site__id=site_id)
        return None # pragma: nocover


class PageWebpathSerializer(TaggitSerializer, serializers.ModelSerializer):
    webpath = WebPathForeignKey()
    tags = TagListSerializerField()

    class Meta:
        model = Page
        fields = '__all__'
        read_only_fields = ['is_active', 'created_by',
                            'modified_by', 'state']


class PageSerializer(TaggitSerializer, serializers.ModelSerializer):
    # webpath = WebPathForeignKey()
    tags = TagListSerializerField()

    class Meta:
        model = Page
        fields = '__all__'
        read_only_fields = ['is_active', 'created_by',
                            'modified_by', 'state']


class PageBlockSerializer(serializers.ModelSerializer):
    page = PageForeignKey()

    class Meta:
        model = PageBlock
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by']


class PageCarouselSerializer(serializers.ModelSerializer):
    page = PageForeignKey()

    class Meta:
        model = PageCarousel
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by']


class PageLinkSerializer(serializers.ModelSerializer):
    page = PageForeignKey()

    class Meta:
        model = PageLink
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by']


class PageLocalizationSerializer(serializers.ModelSerializer):
    page = PageForeignKey()

    class Meta:
        model = PageLocalization
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by']


class PageMenuSerializer(serializers.ModelSerializer):
    page = PageForeignKey()

    class Meta:
        model = PageMenu
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by']


class PageMediaSerializer(serializers.ModelSerializer):
    page = PageForeignKey()

    class Meta:
        model = PageMedia
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by']


class PagePublicationSerializer(serializers.ModelSerializer):
    page = PageForeignKey()

    class Meta:
        model = PagePublication
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by']


class PageRelatedSerializer(serializers.ModelSerializer):
    page = PageForeignKey()

    class Meta:
        model = PageRelated
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by']
