from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from . settings import FORM_SOURCE_LABEL


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


class UniCMSFormSerializer():

    @staticmethod
    def serialize(form):

        def _get_choices(choices):
            elements = []
            for choice in choices:
                if (type(choice[1]) == tuple):
                    elements.extend(_get_choices(choice[1]))
                else:
                    elements.append({"text": choice[1],
                                     "value": choice[0]})
            return elements

        form_fields = []

        for field_name in form.fields:
            field = form.fields[field_name]
            field_type = getattr(field.widget.__class__,
                                 'input_type',
                                 'textarea')

            field_dict = {}
            field_dict['id'] = field_name
            field_dict['label'] = field.label
            field_dict['required'] = 1 if field.required else 0
            field_dict['help_text'] = field.help_text
            field_dict['api_source'] = getattr(field, FORM_SOURCE_LABEL, '')
            field_dict['options'] = []
            field_dict['multiple'] = 0

            class_name = field.widget.__class__.__name__

            if class_name == 'DateInput':
                field_dict['type'] = 'date'
            elif class_name == 'DateTimeInput':
                field_dict['type'] = 'datetime'
            elif class_name in ('Select', 'SelectMultiple'):
                field_dict['type'] = 'select'
                if field.widget.__class__.__dict__.get('allow_multiple_selected'):
                    field_dict['multiple'] = 1

                if hasattr(field, '_queryset') and not getattr(field, FORM_SOURCE_LABEL, ''):
                    for item in field._queryset:
                        field_dict['options'].append({"text": item.__str__(),
                                                      "value": item.pk})
                elif hasattr(field, '_choices'):
                    field_dict['options'].extend(_get_choices(field._choices))
            else:
                field_dict['type'] = field_type
            form_fields.append(field_dict)
        return form_fields


class UniCMSContentTypeClass(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        content_type = ContentType.objects.get_for_model(instance.__class__)
        data['object_content_type'] = content_type.pk
        return data

    class Meta:
        abstract = True


class UniCMSTagsValidator():

    def validate_tags(self, value):
        """
        """
        required = self.fields['tags'].__dict__['required']
        if not value and required:
            raise serializers.ValidationError(_("Field required"))
        return value

    class Meta:
        abstract = True
