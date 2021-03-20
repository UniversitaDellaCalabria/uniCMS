import logging

from django.contrib import admin

from cms.pages.admin import AbstractCreatedModifiedBy
from . admin_inlines import *
from . models import *

logger = logging.getLogger(__name__)


@admin.register(Publication)
class PublicationAdmin(AbstractCreatedModifiedBy):
    search_fields = ('title', 'slug',)
    # list_display = ('title', 'slug', 'date_start', 'date_end', 'is_active',)
    list_display = ('title', 'slug', 'is_active',)
    # list_filter = ('state', 'is_active',
    # 'created', 'modified', 'date_start', 'date_end')
    list_filter = ('is_active', 'created', 'modified')
    inlines = (PublicationLocalizationInline,
               PublicationContextInline,
               PublicationRelatedInline,
               PublicationLinkInline,
               PublicationAttachmentInline,
               PublicationGalleryInline,
               PublicationBlockInline)
    raw_id_fields = ('presentation_image',)

    class Media:
        js = ("js/ckeditor5/ckeditor.js",
              "js/ckeditor-init.js",
        )


@admin.register(PublicationLocalization)
class PublicationLocalizationAdmin(AbstractCreatedModifiedBy):
    search_fields = ('publication__title', 'publication__slug')
    list_display = ('publication', 'language', 'is_active',)
    # list_filter = ('publication__state', 'is_active',
    # 'created', 'modified', 'language')
    list_filter = ('is_active', 'created', 'modified', 'language')


@admin.register(Category)
class CategoryAdmin(AbstractCreatedModifiedBy):
    list_display = ('name', 'image_as_html')

    # def delete_model(modeladmin, request, queryset):
    # obj.delete()
