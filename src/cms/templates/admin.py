from django.contrib import admin

from . models import PageTemplate, PageTemplateBlock, TemplateBlock
from cms.contexts.utils import fill_created_modified_by


class AbstractCreatedModifiedBySave(object):

    def save_model(self, request, obj, form, change): # pragma: no cover
        fill_created_modified_by(request, obj)
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        form.save_m2m()
        for formset in formsets:
            self.save_formset(request, form, formset, change=change)
            if not formset.queryset: continue
            if hasattr(formset.queryset[0], 'modified_by'):
                formset.queryset.update(modified_by = request.user)
            if hasattr(formset.queryset[0], 'created_by'):
                formset.queryset.update(created_by = request.user)


class AbstractCreatedModifiedBy(AbstractCreatedModifiedBySave, admin.ModelAdmin):
    readonly_fields = ('created_by', 'modified_by')


class AbstractCreatedModifiedByTabInline(admin.TabularInline):
    readonly_fields = ('created_by', 'modified_by')


class PageTemplateBlockInline(AbstractCreatedModifiedByTabInline):
    model = PageTemplateBlock
    extra = 0
    raw_id_fields = ('block', )


@admin.register(PageTemplate)
class PageTemplateAdmin(AbstractCreatedModifiedBy):
    list_display = ('name', 'template_file', 'created', 'is_active',
                    'image_as_html')
    search_fields = ('name', 'template_file',)
    inlines = (PageTemplateBlockInline,)


# @admin.register(PageTemplateBlock)
class PageTemplateBlockAdmin(AbstractCreatedModifiedBy):
    list_display = ('block', 'section', 'order', 'is_active')
    # search_fields = ('block__name')
    # list_filter = ('type', 'section')


@admin.register(TemplateBlock)
class TemplateBlockAdmin(AbstractCreatedModifiedBy):
    list_display = ('name', 'description', 'type', 'is_active',
                    'image_as_html')
    search_fields = ('name',)
    list_filter = ('type',)
