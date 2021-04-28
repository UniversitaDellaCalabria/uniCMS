from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.pages.forms import PageMenuForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.page import PageRelatedObject, PageRelatedObjectList, PageRelatedObjectLogsView


class PageMenuList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['menu__name']
    ordering_fields = ['id', 'menu__name', 'order', 'is_active']
    serializer_class = PageMenuSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.page:
            return PageMenu.objects.filter(page=self.page)
        return PageMenu.objects.none() # pragma: no cover


class PageMenuView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageMenuSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageMenu.objects.filter(pk=self.pk, page=self.page)
        return items


class PageMenuFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageMenuForm(page_id=kwargs.get('page_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PageMenuLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPageMenuLogs'


class PageMenuLogsView(PageRelatedObjectLogsView):

    schema = PageMenuLogsSchema()

    def get_queryset(self):
        """
        """
        super().get_data()
        item = get_object_or_404(PageMenu.objects.select_related('page'),
                                 pk=self.pk, page=self.page)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(self.pk, content_type_id)
