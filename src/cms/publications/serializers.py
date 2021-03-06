from cms.api.serializers import UniCMSCreateUpdateSerializer

from cms.contexts.models import WebPath

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


class PublicationSerializer(TaggitSerializer, UniCMSCreateUpdateSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Publication
        fields = '__all__'
        read_only_fields = ('is_active', 'created_by', 'modified_by')


class PublicationContextSerializer(UniCMSCreateUpdateSerializer):
    webpath = WebPathForeignKey()

    class Meta:
        model = PublicationContext
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')


class PublicationAttachmentSerializer(serializers.ModelSerializer):
    publication = PublicationForeignKey()

    class Meta:
        model = PublicationAttachment
        fields = '__all__'
        read_only_fields = ('file_size','file_type')


class PublicationBlockSerializer(serializers.ModelSerializer):
    publication = PublicationForeignKey()

    class Meta:
        model = PublicationBlock
        fields = '__all__'


class PublicationGallerySerializer(serializers.ModelSerializer):
    publication = PublicationForeignKey()

    class Meta:
        model = PublicationGallery
        fields = '__all__'


class PublicationLinkSerializer(serializers.ModelSerializer):
    publication = PublicationForeignKey()

    class Meta:
        model = PublicationLink
        fields = '__all__'


class PublicationLocalizationSerializer(UniCMSCreateUpdateSerializer):
    publication = PublicationForeignKey()

    class Meta:
        model = PublicationLocalization
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')


class PublicationRelatedSerializer(serializers.ModelSerializer):
    publication = PublicationForeignKey()

    class Meta:
        model = PublicationRelated
        fields = '__all__'
