from rest_framework import serializers

from . models import Carousel


class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = ['id',
                  'name',
                  'description',
                  'is_active']
