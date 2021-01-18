import nested_admin

from django.contrib import admin

from . models import (PublicationAttachment, PublicationBlock,
                      PublicationContext, PublicationContextRelated,
                      PublicationGallery, PublicationLink,
                      PublicationLocalization)


class PublicationContextRelatedInline(nested_admin.NestedTabularInline):
    model = PublicationContextRelated
    extra = 0
    classes = ['collapse']
    fk_name = "publication_context"
    # raw_id_fields = ('related',)


class PublicationContextInline(nested_admin.NestedTabularInline):
    model = PublicationContext
    extra = 0
    classes = ['collapse']
    readonly_fields = ('created_by', 'modified_by')
    inlines = [PublicationContextRelatedInline]


class PublicationLocalizationInline(nested_admin.NestedStackedInline):
    model = PublicationLocalization
    extra = 0
    classes = ['collapse']


class PublicationAttachmentInline(nested_admin.NestedStackedInline):
    model = PublicationAttachment
    extra = 0
    classes = ['collapse']
    readonly_fields = ('file_size', 'file_type')


class PublicationLinkInline(nested_admin.NestedStackedInline):
    model = PublicationLink
    extra = 0
    fk_name = 'publication'
    classes = ['collapse']


class PublicationGalleryInline(nested_admin.NestedStackedInline):
    model = PublicationGallery
    extra = 0
    classes = ['collapse']
    raw_id_fields = ['collection']


class PublicationBlockInline(nested_admin.NestedTabularInline):
    model = PublicationBlock
    extra = 0
    classes = ['collapse']
    raw_id_fields = ['block']
