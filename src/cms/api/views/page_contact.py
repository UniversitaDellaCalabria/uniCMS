from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.pages.forms import PageContactForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.page import PageRelatedObject, PageRelatedObjectList, PageRelatedObjectLogsView


class PageContactList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['contact__name', 'contact__description',
                     'contact__contact_type']
    ordering_fields = ['id', 'contact__name', 'contact__contact_type',
                       'is_active', 'order']
    serializer_class = PageContactSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.page:
            return PageContact.objects.filter(page=self.page)
        return PageContact.objects.none() # pragma: no cover


class PageContactView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageContactSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageContact.objects.filter(pk=self.pk, page=self.page)
        return items


class PageContactFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageContactForm(page_id=kwargs.get('page_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PageContactLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPageContactLogs'


class PageContactLogsView(PageRelatedObjectLogsView):

    schema = PageContactLogsSchema()

    def get_queryset(self):
        """
        """
        super().get_data()
        item = get_object_or_404(PageContact.objects.select_related('page'),
                                 pk=self.pk, page=self.page)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(self.pk, content_type_id)
