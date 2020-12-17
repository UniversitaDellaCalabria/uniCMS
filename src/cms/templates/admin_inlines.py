from django.contrib import admin

from . models import *


class PageTemplateBlockInline(admin.TabularInline):
    model = PageTemplateBlock
    extra = 0
    raw_id_fields = ('block', )
