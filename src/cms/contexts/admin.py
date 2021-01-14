from django.contrib import admin

from . models import EditorialBoardEditors, EditorialBoardLocks, WebPath, WebSite
from . utils import fill_created_modified_by


class AbstractCreatedModifiedBy(admin.ModelAdmin):
    readonly_fields = ('created_by', 'modified_by')

    def save_model(self, request, obj, form, change):
        fill_created_modified_by(request, obj)
        super().save_model(request, obj, form, change)


class WebPathAdminInline(admin.TabularInline):
    model = WebPath
    extra = 0


@admin.register(WebSite)
class WebSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('domain', 'name')


class EditorialBoardEditorsAdminInline(admin.TabularInline):
    model = EditorialBoardEditors
    extra = 0
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    raw_id_fields = ('user', 'webpath')


@admin.register(WebPath)
class WebPathAdmin(AbstractCreatedModifiedBy):
    list_display = ('name', 'path', 'site', 'is_active')
    list_filter = ('site', 'created', 'modified', 'is_active')
    search_fields = ('name', 'path',)
    readonly_fields = ('fullpath', 'created', 'modified')
    inlines = (EditorialBoardEditorsAdminInline,)
    raw_id_fields = ['parent', 'alias']


@admin.register(EditorialBoardEditors)
class EditorialBoardEditorsAdmin(AbstractCreatedModifiedBy):
    list_display = ('user', 'permission', 'webpath', 'is_active')
    list_filter = ('permission', 'created', 'modified', 'is_active')
    search_fields = ('user', )
    readonly_fields = ('created', 'modified')


@admin.register(EditorialBoardLocks)
class EditorialBoardLocksAdmin(admin.ModelAdmin):
    list_filter = ('locked_time', )
    list_display = ('content_type', 'object_id',
                    'is_active', 'locked_time', 'locked_by')
