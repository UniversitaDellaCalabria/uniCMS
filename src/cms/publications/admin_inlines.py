from django.contrib import admin

from . models import (PublicationAttachment, PublicationBlock,
                      PublicationContext, PublicationGallery,
                      PublicationLink, PublicationLocalization,
                      PublicationRelated)


class PublicationContextInline(admin.TabularInline):
    model = PublicationContext
    extra = 0
    classes = ['collapse']
    readonly_fields = ('created_by', 'modified_by')


class PublicationLocalizationInline(admin.StackedInline):
    model = PublicationLocalization
    extra = 0
    classes = ['collapse']


class PublicationRelatedInline(admin.TabularInline):
    model = PublicationRelated
    extra = 0
    fk_name = 'publication'
    classes = ['collapse']
    raw_id_fields = ('related',)


class PublicationAttachmentInline(admin.StackedInline):
    model = PublicationAttachment
    extra = 0
    classes = ['collapse']
    readonly_fields = ('file_size', 'file_type')


class PublicationLinkInline(admin.StackedInline):
    model = PublicationLink
    extra = 0
    fk_name = 'publication'
    classes = ['collapse']


class PublicationGalleryInline(admin.TabularInline):
    model = PublicationGallery
    extra = 0
    classes = ['collapse']
    raw_id_fields = ['collection']


class PublicationBlockInline(admin.TabularInline):
    model = PublicationBlock
    extra = 0
    classes = ['collapse']
    raw_id_fields = ['block']
