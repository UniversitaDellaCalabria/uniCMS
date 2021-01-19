from rest_framework import serializers
from . models import Media, MediaCollection, MediaCollectionItem

from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)


class MediaCollectionForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            collection_id = self.context['request'].parser_context['kwargs']['collection_id']
            return MediaCollection.objects.filter(pk=collection_id)
        return None # pragma: no cover


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'


class MediaCollectionSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = MediaCollection
        fields = '__all__'


class MediaCollectionItemSerializer(serializers.ModelSerializer):
    collection = MediaCollectionForeignKey()

    class Meta:
        model = MediaCollectionItem
        fields = '__all__'
