from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.publications.forms import PublicationAttachmentForm
from cms.publications.models import PublicationAttachment
from cms.publications.serializers import PublicationAttachmentSerializer

from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList, PublicationRelatedObjectLogsView


class PublicationAttachmentList(PublicationRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['name', 'file', 'description']
    serializer_class = PublicationAttachmentSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.publication:
            return PublicationAttachment.objects.filter(publication=self.publication)
        return PublicationAttachment.objects.none() # pragma: no cover


class PublicationAttachmentView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationAttachmentSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationAttachment.objects.filter(pk=self.pk,
                                                    publication=self.publication)


class PublicationAttachmentFormView(APIView):

    def get(self, *args, **kwargs):
        form = PublicationAttachmentForm(publication_id=kwargs.get('publication_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PublicationAttachmentLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPublicationAttachmentLogs'


class PublicationAttachmentLogsView(PublicationRelatedObjectLogsView):

    schema = PublicationAttachmentLogsSchema()

    def get_queryset(self):
        """
        """
        super().get_data()
        item = get_object_or_404(PublicationAttachment.objects.select_related('publication'),
                                 pk=self.pk,
                                 publication=self.publication)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(self.pk, content_type_id)
