from cms.api.serializers import (UniCMSCreateUpdateSerializer,
                                 UniCMSContentTypeClass,
                                 UniCMSTagsValidator)

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


class MediaSerializer(UniCMSCreateUpdateSerializer,
                      UniCMSContentTypeClass):
    class Meta:
        model = Media
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by',
                            'file_size', 'file_type')


class MediaCollectionSerializer(TaggitSerializer,
                                UniCMSCreateUpdateSerializer,
                                UniCMSContentTypeClass,
                                UniCMSTagsValidator):
    tags = TagListSerializerField()

    class Meta:
        model = MediaCollection
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')


class MediaCollectionItemSerializer(UniCMSCreateUpdateSerializer,
                                    UniCMSContentTypeClass):
    collection = MediaCollectionForeignKey()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        media = MediaSerializer(instance.media)
        data['media'] = media.data
        return data

    class Meta:
        model = MediaCollectionItem
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')
