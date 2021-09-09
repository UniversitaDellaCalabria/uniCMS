from rest_framework import serializers

from cms.api.serializers import UniCMSContentTypeClass, UniCMSCreateUpdateSerializer

from cms.medias.serializers import MediaSerializer

from . models import *


class ContactForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            contact_id = self.context['request'].parser_context['kwargs']['contact_id']
            return Contact.objects.filter(pk=contact_id)
        return None # pragma: no cover


class ContactInfoForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            contact_id = self.context['request'].parser_context['kwargs']['contact_id']
            item_id = self.context['request'].parser_context['kwargs']['contact_info_id']
            return ContactInfo.objects.filter(pk=item_id,
                                              contact__pk=contact_id)
        return None # pragma: no cover


class ContactSerializer(UniCMSCreateUpdateSerializer,
                        UniCMSContentTypeClass):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        image = MediaSerializer(instance.image)
        data['image'] = image.data
        return data

    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')


class ContactInfoSerializer(UniCMSCreateUpdateSerializer,
                            UniCMSContentTypeClass):
    contact = ContactForeignKey()

    class Meta:
        model = ContactInfo
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')


class ContactLocalizationSerializer(UniCMSCreateUpdateSerializer,
                                    UniCMSContentTypeClass):
    contact = ContactForeignKey()

    class Meta:
        model = ContactLocalization
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')


class ContactInfoLocalizationSerializer(UniCMSCreateUpdateSerializer,
                                        UniCMSContentTypeClass):
    contact_info = ContactInfoForeignKey()

    class Meta:
        model = ContactInfoLocalization
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')


class ContactSelectOptionsSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['value'] = instance.pk
        data['text'] = instance.name
        return data

    class Meta:
        model = Contact
        fields = ()
