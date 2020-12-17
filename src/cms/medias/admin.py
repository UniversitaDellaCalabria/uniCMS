from django.contrib import admin
from django.utils.safestring import mark_safe

from . models import *


class MediaCollectionItemInline(admin.TabularInline):
    model = MediaCollectionItem
    extra = 0


# class MediaLinkInline(admin.TabularInline):
    # model = MediaLink
    # extra = 0


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display  = ('title', 'file_size', 'file_type', 'preview_image')
    list_filter   = ('file_type', 
                     'created', 'modified')
    readonly_fields = ('created_by', 'modified_by', 
                       'file_size', 'file_type')
    inlines = (MediaCollectionItemInline,) # MediaLinkInline)

    readonly_fields = ["headshot_image", "preview_image", 
                       "file_type", "file_size"]

    def headshot_image(self, obj):
        width="55"
        img_tag = f'<img src="{obj.file.url}" style="width: {width}vw;"/>'
        result = mark_safe(img_tag)
        return result

    def preview_image(self, obj):
        width="15"
        img_tag = f'<img src="{obj.file.url}" style="width: {width}vw;"/>'
        result = mark_safe(img_tag)
        return result

@admin.register(MediaCollection)
class MediaCollectionAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    inlines = (MediaCollectionItemInline,)
