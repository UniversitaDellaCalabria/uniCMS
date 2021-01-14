import nested_admin
from django.contrib import admin

from cms.contexts.admin import AbstractCreatedModifiedBy
from . models import NavigationBar, NavigationBarItem, NavigationBarItemLocalization


class NavigationBarItemLocalizationInline(nested_admin.NestedStackedInline):
    model = NavigationBarItemLocalization
    extra = 0
    classes = ['collapse']
    sortable_field_name = ""


class NavigationBarItemInline(nested_admin.NestedStackedInline):
    model = NavigationBarItem
    raw_id_fields = ('parent', 'webpath',
                     'publication', 'inherited_content')
    extra = 0
    # classes = ['collapse']
    inlines = (NavigationBarItemLocalizationInline,)
    sortable_field_name = "order"
    readonly_fields = ('created_by', 'modified_by',)
    fieldsets = (
                (None, {'fields': (('name', 'parent', 'order', 'is_active'),
                                   )}),
                ('weblink', {'fields': (('webpath', 'url', 'publication')),
                             'classes':('collapse',),
                             }
                ),
                ('inherited_content', {'fields': (('inherited_content'),),
                                       'classes':('collapse',)
                                      }
                )
                )


@admin.register(NavigationBar)
class NavigationBarAdmin(AbstractCreatedModifiedBy,
                         nested_admin.NestedModelAdmin):
    list_display = ('name', 'is_active', 'created')
    search_fields = ('name',)
    list_filter = ('created', 'modified')
    readonly_fields = ('created_by', 'modified_by')
    inlines = (NavigationBarItemInline,)


@admin.register(NavigationBarItem)
class NavigationBarItemAdmin(AbstractCreatedModifiedBy,
                             nested_admin.NestedModelAdmin):
    list_display = ('menu', 'name', 'parent', 'is_active')
    search_fields = ('name',)
    list_filter = ('created', 'modified')
    readonly_fields = ('created_by', 'modified_by')
    inlines = (NavigationBarItemLocalizationInline,)
    raw_id_fields = ('menu', )
