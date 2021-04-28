from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.pages.forms import PageMediaForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.page import PageRelatedObject, PageRelatedObjectList, PageRelatedObjectLogsView


class PageMediaList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['media__title', 'media__file', 'media__description']
    ordering_fields = ['id', 'media__title', 'media__file',
                       'media__description', 'order', 'is_active']
    serializer_class = PageMediaSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.page:
            return PageMedia.objects.filter(page=self.page)
        return PageMedia.objects.none() # pragma: no cover


class PageMediaView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageMediaSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageMedia.objects.filter(pk=self.pk, page=self.page)
        return items


class PageMediaFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageMediaForm(page_id=kwargs.get('page_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PageMediaLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPageMediaLogs'


class PageMediaLogsView(PageRelatedObjectLogsView):

    schema = PageMediaLogsSchema()

    def get_queryset(self):
        """
        """
        super().get_data()
        item = get_object_or_404(PageMedia.objects.select_related('page'),
                                 pk=self.pk, page=self.page)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(self.pk, content_type_id)
