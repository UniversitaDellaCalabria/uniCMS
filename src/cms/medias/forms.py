from django.forms import ModelForm
from django.urls import reverse

from cms.api.settings import FORM_SOURCE_LABEL

from . models import Media, MediaCollection, MediaCollectionItem


class MediaForm(ModelForm):

    class Meta:
        model = Media
        fields = ['title', 'file', 'description', 'is_active']


class MediaCollectionForm(ModelForm):

    class Meta:
        model = MediaCollection
        fields = ['name', 'description', 'tags', 'is_active']


class MediaCollectionItemForm(ModelForm):

    def __init__(self, *args, **kwargs):
        collection_id = kwargs.pop('collection_id', None)
        super().__init__(*args, **kwargs)
        if collection_id:
            self.fields['collection'].queryset = MediaCollection.objects.filter(pk=collection_id)
        setattr(self.fields['media'],
                FORM_SOURCE_LABEL,
                reverse('unicms_api:media-options'))

    class Meta:
        model = MediaCollectionItem
        fields = ['collection', 'media', 'order', 'is_active']
