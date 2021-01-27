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


class UniCMSCreateUpdateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        request = self.context['request']
        if request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context['request']
        if request.user:
            validated_data['modified_by'] = request.user
        return super().update(instance, validated_data)

    class Meta:
        abstract = True
