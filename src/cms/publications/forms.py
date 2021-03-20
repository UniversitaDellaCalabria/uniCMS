from django.forms import ModelForm

from . models import Publication, PublicationAttachment, PublicationGallery, PublicationLink, PublicationLocalization, PublicationRelated


class PublicationForm(ModelForm):

    class Meta:
        model = Publication
        fields = ['title', 'subheading', 'content',
                  'presentation_image', 'category',
                  'note', 'tags', 'relevance']


class PublicationAttachmentForm(ModelForm):

    def __init__(self, *args, **kwargs):
        publication_id = kwargs.pop('publication_id', None)
        super().__init__(*args, **kwargs)
        if publication_id:
            self.fields['publication'].queryset = Publication.objects.filter(pk=publication_id)

    class Meta:
        model = PublicationAttachment
        fields = ['publication', 'name', 'file', 'description',
                  'order', 'is_active']


class PublicationGalleryForm(ModelForm):

    def __init__(self, *args, **kwargs):
        publication_id = kwargs.pop('publication_id', None)
        super().__init__(*args, **kwargs)
        if publication_id:
            self.fields['publication'].queryset = Publication.objects.filter(pk=publication_id)

    class Meta:
        model = PublicationGallery
        fields = ['publication', 'collection', 'order', 'is_active']


class PublicationLinkForm(ModelForm):

    def __init__(self, *args, **kwargs):
        publication_id = kwargs.pop('publication_id', None)
        super().__init__(*args, **kwargs)
        if publication_id:
            self.fields['publication'].queryset = Publication.objects.filter(pk=publication_id)

    class Meta:
        model = PublicationLink
        fields = ['publication', 'name', 'url']


class PublicationLocalizationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        publication_id = kwargs.pop('publication_id', None)
        super().__init__(*args, **kwargs)
        if publication_id:
            self.fields['publication'].queryset = Publication.objects.filter(pk=publication_id)

    class Meta:
        model = PublicationLocalization
        fields = ['publication', 'title', 'language', 'subheading',
                  'content', 'is_active']


class PublicationRelatedForm(ModelForm):

    def __init__(self, *args, **kwargs):
        publication_id = kwargs.pop('publication_id', None)
        super().__init__(*args, **kwargs)
        if publication_id:
            self.fields['publication'].queryset = Publication.objects.filter(pk=publication_id)

    class Meta:
        model = PublicationRelated
        fields = ['publication', 'related', 'is_active']