from rest_framework import serializers

from cms.publications.models import *


class PublicationContextSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PublicationContext
        # fields = ['webpath', 
                  # 'publication__date_start',
                  # 'publication__title',
                  # 'publication__subheading',
                  # 'publication__content']
        fields = '__all__'
        lookup_field = 'pk'


class PublicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Publication
        fields = ['date_start',
                  'title',
                  'subheading',
                  'content',
                  # 'tags',
                  # 'categories'
                  ]
