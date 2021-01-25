from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import filters, generics
from rest_framework.permissions import IsAdminUser

from cms.pages.models import *
from cms.pages.serializers import *

from .. exceptions import LoggedPermissionDenied
from .. pagination import UniCmsApiPagination
from .. views.page import PageRelatedObject, PageRelatedObjectList


class PageMediaList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['block__name']
    serializer_class = PageMediaSerializer

    def get_queryset(self):
        """
        """
        super().get_queryset()
        items = PageMedia.objects.filter(page=self.page)
        return items


class PageMediaView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageMediaSerializer

    def get_queryset(self):
        """
        """
        super().get_queryset()
        items = PageMedia.objects.filter(pk=self.pk, page=self.page)
        return items


