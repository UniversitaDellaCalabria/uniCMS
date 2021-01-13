# import logging
# import os

# from django.core.exceptions import ValidationError
# from django.http import HttpResponseRedirect
# from django.shortcuts import get_object_or_404
# from django.urls import reverse
# from django.utils.decorators import method_decorator
# from django.utils.translation import gettext_lazy as _

# from rest_framework import generics, status
# from rest_framework.permissions import IsAdminUser
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from cms.api.serializers import PublicationSerializer, settings

# from cms.carousels.models import *
# from cms.carousels.serializers import *

# from cms.contexts.decorators import detect_language
# from cms.contexts.models import EditorialBoardEditors, WebPath, WebSite
# from cms.contexts.serializers import WebPathSerializer
# from cms.contexts import settings as contexts_settings

# from cms.medias.models import Media
# from cms.medias.serializers import MediaSerializer

# from cms.publications.models import Publication, PublicationContext
# from cms.publications.paginators import Paginator
# from cms.publications.utils import publication_context_base_filter

# from . pagination import UniCmsApiPagination
# from . permissions import (UserCanAddCarouselOrAdminReadonly,
# UserCanAddMediaOrAdminReadonly)
# from . utils import check_user_permission_on_object


# CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
# contexts_settings.CMS_CONTEXT_PERMISSIONS)

# logger = logging.getLogger(__name__)


# @method_decorator(staff_member_required, name='dispatch')
# class EditorWebsitePages(APIView):
# """
# """
# description = ""

# def get(self, request, site_id):
# result = {}
# site = get_object_or_404(WebSite,
# pk=site_id,
# is_active=True)
# result['site_name'] = site.name
# result['site_domain'] = site.domain
# result['pages'] = {}

# lang = getattr(request, 'LANGUAGE_CODE', '')
# pages = {}

# pages_list = Page.objects.filter(webpath__site=site)
# for page in pages_list:
# page.translate_as(lang)
# pages[page.pk] = {"name": page.name,
# "title": page.title,
# "webpath": page.webpath.__str__(),
# "base_template": page.base_template.__str__(),
# "description": page.description,
# "date_start": page.date_start,
# "date_end": page.date_end,
# "state": page.state,
# "type": page.type,
# "tags": [i.slug for i in page.tags.all()],
# "is_active": page.is_active}
# result['pages'] = pages
# return Response(result)


# @method_decorator(staff_member_required, name='dispatch')
# class EditorWebsitePage(APIView):
# """
# Editor user get website webpath permissions
# """
# description = "Get user\'s editorial boards websites single webpath"

# def get(self, request, site_id, page_id):
# page = get_object_or_404(Page,
# pk=page_id,
# webpath__site__pk=site_id,
# webpath__site__is_active=True)
# result = {}
# result['site_name'] = page.webpath.site.name
# result['site_domain'] = page.webpath.site.domain
# result['name'] = page.name
# result['title'] = page.title
# result['webpath'] = page.webpath.__str__()
# result['base_template'] = page.base_template.__str__()
# result['description'] = page.description
# result['date_start'] = page.date_start
# result['date_end'] = page.date_end
# result['state'] = page.state
# result['type'] = page.type
# result['tags'] = [i.slug for i in page.tags.all()]
# result['is_active'] = page.is_active
# return Response(result)
