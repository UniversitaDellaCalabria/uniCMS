from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import filters, generics
from rest_framework.permissions import IsAdminUser

from cms.pages.models import *
from cms.pages.serializers import *

from .. exceptions import LoggedPermissionDenied
from .. pagination import UniCmsApiPagination
from .. views.page import PageRelatedObject, PageRelatedObjectList


class PageBlockList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['block__name']
    serializer_class = PageBlockSerializer

    def get_queryset(self):
        """
        """
        super().get_queryset()
        items = PageBlock.objects.filter(page=self.page)
        return items


class PageBlockView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageBlockSerializer

    def get_queryset(self):
        """
        """
        super().get_queryset()
        items = PageBlock.objects.filter(pk=self.pk, page=self.page)
        return items


