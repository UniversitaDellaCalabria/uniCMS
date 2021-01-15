from cms.contexts.models import WebPath

from rest_framework import serializers
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)

from . models import Publication, PublicationContext


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
        fields = ['id',
                  'title',
                  'slug',
                  'subheading',
                  'content',
                  'content_type',
                  'presentation_image',
                  'state',
                  'date_start',
                  'date_end',
                  'category',
                  'note',
                  'tags',
                  'relevance',
                  'is_active']


class PublicationContextSerializer(serializers.ModelSerializer):
    webpath = WebPathForeignKey()
    publication = PublicationSerializer()

    class Meta:
        model = PublicationContext
        fields = ['id',
                  'publication',
                  'webpath',
                  'in_evidence_start',
                  'in_evidence_end',
                  'is_active']
