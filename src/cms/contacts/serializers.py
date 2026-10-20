from rest_framework import serializers

from cms.api.serializers import UniCMSContentTypeClass, UniCMSCreateUpdateSerializer

from cms.contexts.validators import validate_safe_url
from cms.medias.serializers import MediaSerializer

from . models import *


class ContactForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            contact_id = self.context['request'].parser_context['kwargs']['contact_id']
            return Contact.objects.filter(pk=contact_id)
        return None


class ContactInfoForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            contact_id = self.context['request'].parser_context['kwargs']['contact_id']
            item_id = self.context['request'].parser_context['kwargs']['contact_info_id']
            return ContactInfo.objects.filter(pk=item_id,
                                              contact__pk=contact_id)
        return None


class ContactSerializer(UniCMSCreateUpdateSerializer,
                        UniCMSContentTypeClass):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.image:
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

    def validate(self, attrs):
        info_type = attrs.get('info_type', getattr(self.instance, 'info_type', None))
        value = attrs.get('value', getattr(self.instance, 'value', ''))
        if info_type == 'website':
            validate_safe_url(value)
        return super().validate(attrs)

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

    def validate(self, attrs):
        contact_info = attrs.get('contact_info', getattr(self.instance, 'contact_info', None))
        value = attrs.get('value', getattr(self.instance, 'value', ''))
        if contact_info and contact_info.info_type == 'website':
            validate_safe_url(value)
        return super().validate(attrs)

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
