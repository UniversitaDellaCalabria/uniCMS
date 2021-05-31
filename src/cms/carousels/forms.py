from django.forms import ModelForm
from django.urls import reverse

from cms.api.settings import FORM_SOURCE_LABEL

from . models import Carousel, CarouselItem, CarouselItemLink, CarouselItemLinkLocalization, CarouselItemLocalization


class CarouselForm(ModelForm):

    class Meta:
        model = Carousel
        fields = ['name', 'description', 'is_active']


class CarouselItemForm(ModelForm):

    def __init__(self, *args, **kwargs):
        carousel_id = kwargs.pop('carousel_id', None)
        super().__init__(*args, **kwargs)
        if carousel_id:
            self.fields['carousel'].queryset = Carousel.objects.filter(pk=carousel_id)
        setattr(self.fields['image'],
                FORM_SOURCE_LABEL,
                # only images
                reverse('unicms_api:media-options') + '?file_type=image%2Fwebp')

    class Meta:
        model = CarouselItem
        fields = ['carousel', 'image', 'pre_heading',
                  'heading', 'description', 'order', 'is_active']


class CarouselItemLocalizationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        carousel_id = kwargs.pop('carousel_id', None)
        carousel_item_id = kwargs.pop('carousel_item_id', None)
        super().__init__(*args, **kwargs)
        if carousel_id and carousel_item_id:
            self.fields['carousel_item'].queryset = CarouselItem.objects.filter(pk=carousel_item_id,
                                                                                carousel__pk=carousel_id)

    class Meta:
        model = CarouselItemLocalization
        fields = ['carousel_item', 'language', 'pre_heading',
                  'heading', 'description', 'order', 'is_active']


class CarouselItemLinkForm(ModelForm):

    def __init__(self, *args, **kwargs):
        carousel_id = kwargs.pop('carousel_id', None)
        carousel_item_id = kwargs.pop('carousel_item_id', None)
        super().__init__(*args, **kwargs)
        if carousel_id and carousel_item_id:
            self.fields['carousel_item'].queryset = CarouselItem.objects.filter(pk=carousel_item_id,
                                                                                carousel__pk=carousel_id)

    class Meta:
        model = CarouselItemLink
        fields = ['carousel_item', 'title_preset', 'title',
                  'url', 'order', 'is_active']


class CarouselItemLinkLocalizationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        carousel_id = kwargs.pop('carousel_id', None)
        carousel_item_id = kwargs.pop('carousel_item_id', None)
        carousel_item_link_id = kwargs.pop('carousel_item_link_id', None)
        super().__init__(*args, **kwargs)
        if carousel_id and carousel_item_id:
            self.fields['carousel_item_link'].queryset = CarouselItemLink.objects.filter(pk=carousel_item_link_id,
                                                                                         carousel_item__pk=carousel_item_id,
                                                                                         carousel_item__carousel__pk=carousel_id)

    class Meta:
        model = CarouselItemLinkLocalization
        fields = ['carousel_item_link', 'language', 'title',
                  'order', 'is_active']
