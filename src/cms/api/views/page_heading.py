from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.pages.forms import PageHeadingForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.page import PageRelatedObject, PageRelatedObjectList, PageRelatedObjectLogsView


class PageHeadingList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['title', 'description']
    serializer_class = PageHeadingSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.page:
            return PageHeading.objects.filter(page=self.page)
        return PagePublication.objects.none() # pragma: no cover


class PageHeadingView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageHeadingSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageHeading.objects.filter(pk=self.pk, page=self.page)
        return items


class PageHeadingFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageHeadingForm(page_id=kwargs.get('page_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PageHeadingLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPageHeadingLogs'


class PageHeadingLogsView(PageRelatedObjectLogsView):

    schema = PageHeadingLogsSchema()

    def get_queryset(self):
        """
        """
        super().get_data()
        item = get_object_or_404(PageHeading.objects.select_related('page'),
                                 pk=self.pk, page=self.page)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(self.pk, content_type_id)
