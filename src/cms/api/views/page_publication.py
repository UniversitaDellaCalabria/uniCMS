from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.pages.forms import PagePublicationForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.page import PageRelatedObject, PageRelatedObjectList, PageRelatedObjectLogsView


class PagePublicationList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['publication__name','publication__title',
                     'publication__subheading', 'publication__content']
    ordering_fields = ['id', 'publication__name', 'publication__title',
                       'publication__subheading', 'order', 'is_active']
    serializer_class = PagePublicationSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.page:
            return PagePublication.objects.filter(page=self.page)
        return PagePublication.objects.none() # pragma: no cover


class PagePublicationView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PagePublicationSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PagePublication.objects.filter(pk=self.pk, page=self.page)
        return items


class PagePublicationFormView(APIView):

    def get(self, *args, **kwargs):
        form = PagePublicationForm(page_id=kwargs.get('page_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PagePublicationSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPagePublicationLogs'


class PagePublicationLogsView(PageRelatedObjectLogsView):

    schema = PagePublicationSchema()

    def get_queryset(self):
        """
        """
        super().get_data()
        item = get_object_or_404(PagePublication.objects.select_related('page'),
                                 pk=self.pk, page=self.page)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(self.pk, content_type_id)
