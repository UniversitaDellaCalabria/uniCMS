from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.pages.forms import PageRelatedForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.page import PageRelatedObject, PageRelatedObjectList, PageRelatedObjectLogsView


class PageRelatedList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['related__name', 'related__title']
    serializer_class = PageRelatedSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.page:
            return PageRelated.objects.filter(page=self.page)
        return PageRelated.objects.none() # pragma: no cover


class PageRelatedView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageRelatedSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageRelated.objects.filter(pk=self.pk, page=self.page)
        return items


class PageRelatedFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageRelatedForm(page_id=kwargs.get('page_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PageRelatedSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPageRelatedLogs'


class PageRelatedLogsView(PageRelatedObjectLogsView):

    schema = PageRelatedSchema()

    def get_queryset(self):
        """
        """
        super().get_data()
        item = get_object_or_404(PageRelated.objects.select_related('page'),
                                 pk=self.pk, page=self.page)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(self.pk, content_type_id)
