from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.publications.forms import PublicationLinkForm
from cms.publications.models import *
from cms.publications.serializers import *

from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList, PublicationRelatedObjectLogsView


class PublicationLinkList(PublicationRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['name', 'url']
    filterset_fields = ['created', 'modified']
    serializer_class = PublicationLinkSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.publication:
            return PublicationLink.objects.filter(publication=self.publication)
        return PublicationLink.objects.none() # pragma: no cover


class PublicationLinkView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationLinkSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationLink.objects.filter(pk=self.pk,
                                              publication=self.publication)


class PublicationLinkFormView(APIView):

    def get(self, *args, **kwargs):
        form = PublicationLinkForm(publication_id=kwargs.get('publication_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PublicationLinkLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPublicationLinkLogs'


class PublicationLinkLogsView(PublicationRelatedObjectLogsView):

    schema = PublicationLinkLogsSchema()

    def get_queryset(self):
        """
        """
        super().get_data()
        item = get_object_or_404(PublicationLink.objects.select_related('publication'),
                                 pk=self.pk,
                                 publication=self.publication)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(self.pk, content_type_id)
