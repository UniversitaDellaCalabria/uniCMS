from django.forms import ModelForm

from cms.pages.models import Page, PageBlock, PageCarousel, PageLink, PageLocalization, PageMedia, PageMenu, PagePublication, PageRelated

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

    class Meta:
        model = PageMedia
        fields = ['page', 'media', 'url', 'order', 'is_active']


class PageLinkForm(ModelForm):

    def __init__(self, *args, **kwargs):
        page_id = kwargs.pop('page_id', None)
        super().__init__(*args, **kwargs)
        if page_id:
            self.fields['page'].queryset = Page.objects.filter(pk=page_id)

    class Meta:
        model = PageLink
        fields = ['page', 'name', 'url']


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
        fields = ['page', 'menu', 'section', 'order', 'is_active']


class PagePublicationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        page_id = kwargs.pop('page_id', None)
        super().__init__(*args, **kwargs)
        if page_id:
            self.fields['page'].queryset = Page.objects.filter(pk=page_id)

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
