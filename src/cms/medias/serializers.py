from rest_framework import serializers
from . models import Media, MediaCollection, MediaCollectionItem

from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id',
                  'title',
                  'file',
                  'description',
                  'is_active']


class MediaCollectionSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = MediaCollection
        fields = ['id',
                  'name',
                  'description',
                  'tags',
                  'is_active']


class MediaCollectionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaCollectionItem
        fields = ['id',
                  'media',
                  'collection',
                  'is_active']
