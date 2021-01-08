import nested_admin

from django.contrib import admin

from . models import Page, PageBlock, PageCarousel, PageLink, PageLocalization, PageMedia, PageMenu, PagePublication, PageRelated


class PageInline(admin.TabularInline):
    model = Page
    extra = 0
    classes = ['collapse']


class PageLocalizationInline(nested_admin.NestedStackedInline):
    model = PageLocalization
    extra = 0
    classes = ['collapse']


class PageLinkInline(nested_admin.NestedTabularInline):
    model = PageLink
    extra = 0
    classes = ['collapse']
    sortable_field_name = "order"


class PageRelatedInline(nested_admin.NestedTabularInline):
    model = PageRelated
    fk_name = 'page'
    autocomplete_fields = ('related_page',)
    extra = 0
    classes = ['collapse']
    sortable_field_name = "order"


class PageBlockInline(nested_admin.NestedTabularInline):
    model = PageBlock
    extra = 0
    raw_id_fields = ('block',)
    sortable_field_name = "order"


class PagePublicationInline(nested_admin.NestedTabularInline):
    model = PagePublication
    extra = 0
    raw_id_fields = ('publication',)
    sortable_field_name = "order"


class PageCarouselInline(nested_admin.NestedTabularInline):
    model = PageCarousel
    extra = 0
    classes = ['collapse']
    raw_id_fields = ("carousel",)
    sortable_field_name = "order"


class PageMediaInline(nested_admin.NestedTabularInline):
    model = PageMedia
    extra = 0
    classes = ['collapse']
    raw_id_fields = ("media",)
    sortable_field_name = "order"


class PageMenuInline(nested_admin.NestedTabularInline):
    model = PageMenu
    extra = 0
    classes = ['collapse']
    raw_id_fields = ("menu",)
    sortable_field_name = "order"
