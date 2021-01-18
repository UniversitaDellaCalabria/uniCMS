from cms.contexts.models import WebPath
from cms.pages.models import Category

from rest_framework import serializers
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)

from . models import *


class PublicationForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            publication_id = self.context['request'].parser_context['kwargs']['publication_id']
            return Publication.objects.filter(pk=publication_id)
        return None


class WebPathForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            site_id = self.context['request'].parser_context['kwargs']['site_id']
            webpath_id = self.context['request'].parser_context['kwargs']['webpath_id']
            return WebPath.objects.filter(pk=webpath_id,
                                          site__id=site_id)
        return None


class PublicationSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Publication
        fields = '__all__'
        read_only_fields = ['is_active']


class PublicationContextFullSerializer(serializers.ModelSerializer):
    webpath = WebPathForeignKey()
    publication = PublicationSerializer()

    # nested serializers need custom create() method
    def create(self, validated_data):
        pub_data = validated_data.pop('publication')
        categories = pub_data.pop('category')
        pub = Publication.objects.create(**pub_data)
        # many-to-many relation on category
        pub.category.set(categories)
        pub_cxt = PublicationContext.objects.create(**validated_data,
                                                    publication=pub)
        return pub_cxt

    class Meta:
        model = PublicationContext
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by']


class PublicationContextSerializer(serializers.ModelSerializer):
    webpath = WebPathForeignKey()

    class Meta:
        model = PublicationContext
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by']


class PublicationAttachmentSerializer(serializers.ModelSerializer):
    publication = PublicationForeignKey()

    class Meta:
        model = PublicationAttachment
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by',
                            'file_size','file_type']


class PublicationGallerySerializer(serializers.ModelSerializer):
    publication = PublicationForeignKey()

    class Meta:
        model = PublicationGallery
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by']


class PublicationLinkSerializer(serializers.ModelSerializer):
    publication = PublicationForeignKey()

    class Meta:
        model = PublicationLink
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by']


class PublicationLocalizationSerializer(serializers.ModelSerializer):
    publication = PublicationForeignKey()

    class Meta:
        model = PublicationLocalization
        fields = '__all__'
        read_only_fields = ['created_by', 'modified_by']
