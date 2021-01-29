from cms.api.serializers import UniCMSCreateUpdateSerializer

from rest_framework import serializers

from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)

from . models import Media, MediaCollection, MediaCollectionItem


class MediaCollectionForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            collection_id = self.context['request'].parser_context['kwargs']['collection_id']
            return MediaCollection.objects.filter(pk=collection_id)
        return None # pragma: no cover


class MediaSerializer(UniCMSCreateUpdateSerializer):
    class Meta:
        model = Media
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by',
                            'file_size', 'file_type')


class MediaCollectionSerializer(TaggitSerializer, UniCMSCreateUpdateSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = MediaCollection
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')


class MediaCollectionItemSerializer(UniCMSCreateUpdateSerializer):
    collection = MediaCollectionForeignKey()

    class Meta:
        model = MediaCollectionItem
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')
