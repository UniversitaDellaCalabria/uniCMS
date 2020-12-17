from django.contrib import admin

from . admin_inlines import *
from . models import *


@admin.register(PageTemplate)
class PageTemplateAdmin(admin.ModelAdmin):
    list_display  = ('name', 'template_file', 'created', 'is_active')
    search_fields   = ('name', 'template_file',)
    inlines       = (PageTemplateBlockInline,)


# @admin.register(PageTemplateBlock)
class PageTemplateBlockAdmin(admin.ModelAdmin):
    list_display  = ('block', 'section', 'order', 'is_active')
    # search_fields   = ('block__name')
    # list_filter = ('type', 'section')


@admin.register(TemplateBlock)
class TemplateBlockAdmin(admin.ModelAdmin):
    list_display  = ('name', 'description', 'type', 'is_active')
    search_fields   = ('name',)
    list_filter = ('type',)
