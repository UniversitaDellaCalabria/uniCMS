from django.forms import ModelForm
from django.urls import reverse

from cms.api.settings import FORM_SOURCE_LABEL

from . models import Contact, ContactInfo, ContactInfoLocalization, ContactLocalization


class ContactForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self.fields['image'],
                FORM_SOURCE_LABEL,
                # only images
                reverse('unicms_api:media-options') + '?file_type=image%2Fwebp')

    class Meta:
        model = Contact
        fields = ['name', 'description', 'image', 'contact_type', 'is_active']


class ContactInfoForm(ModelForm):

    def __init__(self, *args, **kwargs):
        contact_id = kwargs.pop('contact_id', None)
        super().__init__(*args, **kwargs)
        if contact_id:
            self.fields['contact'].queryset = Contact.objects.filter(pk=contact_id)

    class Meta:
        model = ContactInfo
        fields = ['contact', 'info_type', 'label', 'value', 'order', 'is_active']


class ContactLocalizationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        contact_id = kwargs.pop('contact_id', None)
        super().__init__(*args, **kwargs)
        if contact_id:
            self.fields['contact'].queryset = Contact.objects.filter(pk=contact_id)

    class Meta:
        model = ContactLocalization
        fields = ['contact', 'language', 'name',
                  'description', 'order', 'is_active']


class ContactInfoLocalizationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        contact_id = kwargs.pop('contact_id', None)
        contact_info_id = kwargs.pop('contact_info_id', None)
        super().__init__(*args, **kwargs)
        if contact_id and contact_info_id:
            self.fields['contact_info'].queryset = ContactInfo.objects.filter(pk=contact_info_id,
                                                                              contact=contact_id)

    class Meta:
        model = ContactInfoLocalization
        fields = ['contact_info', 'language', 'label',
                  'value', 'order', 'is_active']
