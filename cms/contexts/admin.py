import json

from copy import deepcopy
from django.contrib import admin
from django.contrib import messages
from django.forms.utils import ErrorList
from django.http import (HttpResponse,
                         Http404,
                         HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _

from . models import *


class AbstractCreatedModifiedBy(admin.ModelAdmin):
    readonly_fields = ('created_by', 'modified_by')


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
class WebPathAdmin(admin.ModelAdmin):
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
