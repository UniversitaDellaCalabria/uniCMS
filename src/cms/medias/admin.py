from django.contrib import admin
from django.utils.safestring import mark_safe

from cms.contexts.admin import AbstractCreatedModifiedBy
from . models import Media, MediaCollection, MediaCollectionItem


def preview_image(obj):
    width = "15"
    img_tag = f'<img src="{obj.file.url}" style="width: {width}vw;"/>'
    result = mark_safe(img_tag) # nosec
    return result


class MediaCollectionItemInline(admin.TabularInline):
    model = MediaCollectionItem
    readonly_fields = ('created_by', 'modified_by', 'preview_image')
    extra = 0

    def preview_image(self, obj):
        return preview_image(obj) # nosec


@admin.register(Media)
class MediaAdmin(AbstractCreatedModifiedBy):
    search_fields = ('title',)
    list_display = ('title', 'file_size', 'file_type', 'preview_image')
    list_filter = ('file_type',
                   'created', 'modified')
    inlines = (MediaCollectionItemInline,) # MediaLinkInline)

    readonly_fields = ("headshot_image", "preview_image",
                       "file_type", "file_size",
                       'created_by', 'modified_by')

    def headshot_image(self, obj):
        width = "55"
        img_tag = f'<img src="{obj.file.url}" style="width: {width}vw;"/>'
        result = mark_safe(img_tag) # nosec
        return result

    def preview_image(self, obj):
        return preview_image(obj)


@admin.register(MediaCollection)
class MediaCollectionAdmin(AbstractCreatedModifiedBy):
    search_fields = ('name',)
    readonly_fields = ('created_by', 'modified_by')
    inlines = (MediaCollectionItemInline,)
