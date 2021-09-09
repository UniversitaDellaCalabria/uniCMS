import nested_admin

from django.contrib import admin

from cms.contexts.admin import AbstractCreatedModifiedBy
from . models import Contact, ContactInfo, ContactInfoLocalization, ContactLocalization


class ContactInfoLocalizationInline(nested_admin.NestedStackedInline):
    model = ContactInfoLocalization
    extra = 0
    sortable_field_name = "order"
    classes = ['collapse']


class ContactInfoInline(nested_admin.NestedStackedInline):
    model = ContactInfo
    extra = 0
    sortable_field_name = "order"
    classes = ['collapse']
    inlines = (ContactInfoLocalizationInline,)


class ContactLocalizationInline(nested_admin.NestedStackedInline):
    model = ContactLocalization
    extra = 0
    sortable_field_name = "order"
    classes = ['collapse']


@admin.register(Contact)
class ContactAdmin(AbstractCreatedModifiedBy, nested_admin.NestedModelAdmin):
    list_display = ('name', 'contact_type', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('created', 'modified', 'contact_type')
    inlines = (ContactInfoInline, ContactLocalizationInline)
    readonly_fields = ('created_by', 'modified_by')
