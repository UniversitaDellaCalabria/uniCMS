import logging

from django.contrib import admin, messages
from django.utils.translation import gettext, gettext_lazy as _

from cms.pages.admin import AbstractCreatedModifiedBy
from . admin_inlines import *
from . models import *

logger = logging.getLogger(__name__)


@admin.register(Publication)
class PublicationAdmin(AbstractCreatedModifiedBy):
    search_fields = ('title',)
    list_display  = ('title', 'slug', 'date_start', 'date_end', 'is_active',)
    list_filter   = ('state', 'is_active',
                     'created', 'modified', 'date_start', 'date_end')
    inlines       = (PublicationLocalizationInline,
                     PublicationContextInline,
                     PublicationRelatedInline,
                     PublicationLinkInline,
                     PublicationAttachmentInline,
                     PublicationGalleryInline,
                     PublicationBlockInline)
    raw_id_fields = ('presentation_image',)
    
    class Media:
        js = ("js/ckeditor5/23.1.0/classic/ckeditor.js",
              "js/ckeditor-init.js",)
        # css = {
            # "all": ("my_styles.css",)
        # }

@admin.register(PublicationLocalization)
class PublicationLocalizationAdmin(AbstractCreatedModifiedBy):
    search_fields = ('publication__title',)
    list_display  = ('publication', 'language', 'is_active',)
    list_filter   = ('publication__state', 'is_active',
                     'created', 'modified', 'language')
