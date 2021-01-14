import nested_admin

from django.contrib import admin

from cms.contexts.admin import AbstractCreatedModifiedBy
from . models import Carousel, CarouselItem, CarouselItemLink, CarouselItemLinkLocalization, CarouselItemLocalization


class CarouselItemLinkLocalizationInline(nested_admin.NestedStackedInline):
    model = CarouselItemLinkLocalization
    extra = 0
    sortable_field_name = "order"
    classes = ['collapse']


class CarouselItemLinkInline(nested_admin.NestedStackedInline):
    model = CarouselItemLink
    extra = 0
    sortable_field_name = "order"
    classes = ['collapse']
    inlines = (CarouselItemLinkLocalizationInline,)


class CarouselItemLocalizationInline(nested_admin.NestedStackedInline):
    model = CarouselItemLocalization
    extra = 0
    sortable_field_name = "order"
    classes = ['collapse']


class CarouselItemInline(nested_admin.NestedStackedInline):
    model = CarouselItem
    extra = 0
    inlines = (CarouselItemLocalizationInline, CarouselItemLinkInline,)
    sortable_field_name = "order"
    classes = ['collapse']
    raw_id_fields = ('image',)


@admin.register(Carousel)
class CarouselAdmin(AbstractCreatedModifiedBy, nested_admin.NestedModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('created', 'modified')
    inlines = (CarouselItemInline,)
    readonly_fields = ('created_by', 'modified_by')
