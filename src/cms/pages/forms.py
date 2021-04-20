from django.forms import ModelForm
from django.urls import reverse

from cms.api.settings import FORM_SOURCE_LABEL
from cms.pages.models import (Page,
                              PageBlock,
                              PageCarousel,
                              PageHeading,
                              PageHeadingLocalization,
                              PageLink,
                              PageLocalization,
                              PageMedia,
                              PageMediaCollection,
                              PageMenu,
                              PagePublication,
                              PageRelated)

from . models import WebPath, WebSite


class PageForm(ModelForm):

    def __init__(self, *args, **kwargs):
        site_id = kwargs.pop('site_id', None)
        webpath_id = kwargs.pop('webpath_id', None)
        super().__init__(*args, **kwargs)
        if site_id:
            if webpath_id:
                self.fields['webpath'].queryset = WebPath.objects.filter(pk=webpath_id,
                                                                         site__pk=site_id)
            else:
                self.fields['webpath'].queryset = WebPath.objects.filter(site__pk=site_id)
            setattr(self.fields['webpath'],
                    FORM_SOURCE_LABEL,
                    reverse('unicms_api:webpath-options',
                            kwargs={'site_id': site_id}))

    class Meta:
        model = Page
        fields = ['webpath', 'name', 'title',
                  'base_template', 'description',
                  'date_start', 'date_end',
                  'type', 'tags']


class PageBlockForm(ModelForm):

    def __init__(self, *args, **kwargs):
        page_id = kwargs.pop('page_id', None)
        super().__init__(*args, **kwargs)
        if page_id:
            self.fields['page'].queryset = Page.objects.filter(pk=page_id)

    class Meta:
        model = PageBlock
        fields = ['page', 'block', 'section', 'order', 'is_active']


class PageCarouselForm(ModelForm):

    def __init__(self, *args, **kwargs):
        page_id = kwargs.pop('page_id', None)
        super().__init__(*args, **kwargs)
        if page_id:
            self.fields['page'].queryset = Page.objects.filter(pk=page_id)

    class Meta:
        model = PageCarousel
        fields = ['page', 'carousel', 'order', 'is_active']


class PageMediaForm(ModelForm):

    def __init__(self, *args, **kwargs):
        page_id = kwargs.pop('page_id', None)
        super().__init__(*args, **kwargs)
        if page_id:
            self.fields['page'].queryset = Page.objects.filter(pk=page_id)
        setattr(self.fields['media'],
                FORM_SOURCE_LABEL,
                reverse('unicms_api:media-options'))

    class Meta:
        model = PageMedia
        fields = ['page', 'media', 'url', 'order', 'is_active']


class PageMediaCollectionForm(ModelForm):

    def __init__(self, *args, **kwargs):
        page_id = kwargs.pop('page_id', None)
        super().__init__(*args, **kwargs)
        if page_id:
            self.fields['page'].queryset = Page.objects.filter(pk=page_id)

    class Meta:
        model = PageMediaCollection
        fields = ['page', 'collection', 'order', 'is_active']


class PageLinkForm(ModelForm):

    def __init__(self, *args, **kwargs):
        page_id = kwargs.pop('page_id', None)
        super().__init__(*args, **kwargs)
        if page_id:
            self.fields['page'].queryset = Page.objects.filter(pk=page_id)

    class Meta:
        model = PageLink
        fields = ['page', 'name', 'url', 'order']


class PageLocalizationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        page_id = kwargs.pop('page_id', None)
        super().__init__(*args, **kwargs)
        if page_id:
            self.fields['page'].queryset = Page.objects.filter(pk=page_id)

    class Meta:
        model = PageLocalization
        fields = ['page', 'title', 'language', 'is_active']


class PageMenuForm(ModelForm):

    def __init__(self, *args, **kwargs):
        page_id = kwargs.pop('page_id', None)
        super().__init__(*args, **kwargs)
        if page_id:
            self.fields['page'].queryset = Page.objects.filter(pk=page_id)

    class Meta:
        model = PageMenu
        fields = ['page', 'menu',  # 'section',
                  'order', 'is_active']


class PagePublicationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        page_id = kwargs.pop('page_id', None)
        super().__init__(*args, **kwargs)
        if page_id:
            self.fields['page'].queryset = Page.objects.filter(pk=page_id)
        setattr(self.fields['publication'],
                FORM_SOURCE_LABEL,
                reverse('unicms_api:editorial-board-publications-options'))

    class Meta:
        model = PagePublication
        fields = ['page', 'publication', 'order', 'is_active']


class PageRelatedForm(ModelForm):

    def __init__(self, *args, **kwargs):
        page_id = kwargs.pop('page_id', None)
        super().__init__(*args, **kwargs)
        if page_id:
            self.fields['page'].queryset = Page.objects.filter(pk=page_id)

    class Meta:
        model = PageRelated
        fields = ['page', 'related_page', 'order', 'is_active']


class PageHeadingForm(ModelForm):

    def __init__(self, *args, **kwargs):
        page_id = kwargs.pop('page_id', None)
        super().__init__(*args, **kwargs)
        if page_id:
            self.fields['page'].queryset = Page.objects.filter(pk=page_id)

    class Meta:
        model = PageHeading
        fields = ['page', 'title', 'description', 'order', 'is_active']


class PageHeadingLocalizationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        page_id = kwargs.pop('page_id', None)
        heading_id = kwargs.pop('heading_id', None)
        super().__init__(*args, **kwargs)
        if page_id and heading_id:
            self.fields['heading'].queryset = PageHeading.objects.filter(pk=heading_id,
                                                                         page__pk=page_id)

    class Meta:
        model = PageHeadingLocalization
        fields = ['heading', 'title', 'description', 'language',
                  'order', 'is_active']
