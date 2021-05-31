from cms.api.serializers import (UniCMSCreateUpdateSerializer,
                                 UniCMSContentTypeClass,
                                 UniCMSTagsValidator)

from rest_framework import serializers

from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)

from . models import Media, MediaCollection, MediaCollectionItem
from . utils import get_image_width_height


class MediaCollectionForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            collection_id = self.context['request'].parser_context['kwargs']['collection_id']
            return MediaCollection.objects.filter(pk=collection_id)
        return None # pragma: no cover


class MediaSerializer(UniCMSCreateUpdateSerializer,
                      UniCMSContentTypeClass):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['file_size'] = instance.file_size_kb
        try:
            size = get_image_width_height(instance.file)
            if size:
                w,y = size
                data['file_dimensions'] = f'{w}px*{y}px'
            else:
                data['file_dimensions'] = ''
        except FileNotFoundError: # pragma: no cover
            data['file_dimensions'] = ''
        return data

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


class MediaSelectOptionsSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['value'] = instance.pk
        data['text'] = instance.title
        return data

    class Meta:
        model = Media
        fields = ()


class MediaCollectionSelectOptionsSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['value'] = instance.pk
        data['text'] = instance.name
        return data

    class Meta:
        model = MediaCollection
        fields = ()
