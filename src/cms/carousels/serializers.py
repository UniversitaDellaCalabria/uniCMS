from rest_framework import serializers

from . models import Carousel, CarouselItem, CarouselItemLink, CarouselItemLinkLocalization, CarouselItemLocalization


class CarouselForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            carousel_id = self.context['request'].parser_context['kwargs']['carousel_id']
            return Carousel.objects.filter(pk=carousel_id)
        return None


class CarouselItemForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            carousel_id = self.context['request'].parser_context['kwargs']['carousel_id']
            item_id = self.context['request'].parser_context['kwargs']['carousel_item_id']
            return CarouselItem.objects.filter(pk=item_id,
                                               carousel__pk=carousel_id)
        return None


class CarouselItemLinkForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            carousel_id = self.context['request'].parser_context['kwargs']['carousel_id']
            item_id = self.context['request'].parser_context['kwargs']['carousel_item_id']
            link_id = self.context['request'].parser_context['kwargs']['carousel_item_link_id']
            return CarouselItemLink.objects.filter(pk=link_id,
                                                   carousel_item__pk=item_id,
                                                   carousel_item__carousel__pk=carousel_id)
        return None


class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = ['id',
                  'name',
                  'description',
                  'is_active']


class CarouselItemSerializer(serializers.ModelSerializer):
    carousel = CarouselForeignKey()

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
    carousel_item = CarouselItemForeignKey()

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
    carousel_item = CarouselItemForeignKey()

    class Meta:
        model = CarouselItemLink
        fields = ['id',
                  'carousel_item',
                  'title_preset',
                  'title',
                  'url',
                  'is_active',]


class CarouselItemLinkLocalizationSerializer(serializers.ModelSerializer):
    carousel_item_link = CarouselItemLinkForeignKey()

    class Meta:
        model = CarouselItemLinkLocalization
        fields = ['id',
                  'carousel_item_link',
                  'language',
                  'title',
                  'is_active',]
