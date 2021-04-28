from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.publications.forms import PublicationRelatedForm
from cms.publications.models import *
from cms.publications.serializers import *

from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList, PublicationRelatedObjectLogsView


class PublicationRelatedList(PublicationRelatedObjectList):
    """
    """
    description = ""
    serializer_class = PublicationRelatedSerializer
    search_fields = ['related__name', 'related__title']

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.publication:
            return PublicationRelated.objects.filter(publication=self.publication)
        return PublicationRelated.objects.none() # pragma: no cover


class PublicationRelatedView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationRelatedSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationRelated.objects.filter(pk=self.pk,
                                                 publication=self.publication)


class PublicationRelatedFormView(APIView):

    def get(self, *args, **kwargs):
        form = PublicationRelatedForm(publication_id=kwargs.get('publication_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PublicationRelatedLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPublicationRelatedLogs'


class PublicationRelatedLogsView(PublicationRelatedObjectLogsView):

    schema = PublicationRelatedLogsSchema()

    def get_queryset(self):
        """
        """
        super().get_data()
        item = get_object_or_404(PublicationRelated.objects.select_related('publication'),
                                 pk=self.pk,
                                 publication=self.publication)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(self.pk, content_type_id)
