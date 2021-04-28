from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.pages.forms import PageMediaCollectionForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.page import PageRelatedObject, PageRelatedObjectList, PageRelatedObjectLogsView


class PageMediaCollectionList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['collection__name', 'collection__description']
    ordering_fields = ['id', 'collection__name',
                       'collection__description', 'order', 'is_active']
    serializer_class = PageMediaCollectionSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.page:
            return PageMediaCollection.objects.filter(page=self.page)
        return PageMediaCollection.objects.none() # pragma: no cover


class PageMediaCollectionView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageMediaCollectionSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageMediaCollection.objects.filter(pk=self.pk, page=self.page)
        return items


class PageMediaCollectionFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageMediaCollectionForm(page_id=kwargs.get('page_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PageMediaCollectionLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPageMediaCollectionLogs'


class PageMediaCollectionLogsView(PageRelatedObjectLogsView):

    schema = PageMediaCollectionLogsSchema()

    def get_queryset(self):
        """
        """
        super().get_data()
        item = get_object_or_404(PageMediaCollection.objects.select_related('page'),
                                 pk=self.pk, page=self.page)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(self.pk, content_type_id)
