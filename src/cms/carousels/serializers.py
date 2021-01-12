from rest_framework import serializers

from . models import Carousel, CarouselItem, CarouselItemLink, CarouselItemLinkLocalization, CarouselItemLocalization


class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = ['id',
                  'name',
                  'description',
                  'is_active']


class CarouselItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselItem
        fields = ['id',
                  'carousel',
                  'image',
                  'pre_heading',
                  'heading',
                  'description',
                  'is_active',]


class CarouselItemLocalizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselItemLocalization
        fields = ['id',
                  'carousel_item',
                  'language',
                  'pre_heading',
                  'heading',
                  'description',
                  'is_active',]


class CarouselItemLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselItemLink
        fields = ['id',
                  'carousel_item',
                  'title_preset',
                  'title',
                  'url',
                  'is_active',]


class CarouselItemLinkLocalizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselItemLinkLocalization
        fields = ['id',
                  'carousel_item_link',
                  'language',
                  'title',
                  'is_active',]
