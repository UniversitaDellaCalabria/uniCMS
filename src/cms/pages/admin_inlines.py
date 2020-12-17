from django.contrib import admin

from . models import *


class PageInline(admin.TabularInline):
    model = Page
    extra = 0
    classes = ['collapse']


class PageLinkInline(admin.TabularInline):
    model = PageLink
    extra = 0
    classes = ['collapse']


class PageRelatedInline(admin.TabularInline):
    model = PageRelated
    fk_name = 'page'
    autocomplete_fields = ('related_page',)
    extra = 0
    classes = ['collapse']


class PageBlockInline(admin.TabularInline):
    model = PageBlock
    extra = 0
    raw_id_fields = ('block',)


class PageCarouselInline(admin.TabularInline):
    model = PageCarousel
    extra = 0
    classes = ['collapse']
    raw_id_fields = ("carousel",)


class PageMenuInline(admin.TabularInline):
    model = PageMenu
    extra = 0
    classes = ['collapse']
    raw_id_fields = ("menu",)
