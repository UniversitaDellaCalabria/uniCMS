from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.publications.models import *
from cms.publications.serializers import *

from rest_framework.schemas.openapi import AutoSchema

from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList, PublicationRelatedObjectLogsView


class PublicationBlockList(PublicationRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['block__name']
    serializer_class = PublicationBlockSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.publication:
            return PublicationBlock.objects.filter(publication=self.publication)
        return PublicationBlock.objects.none() # pragma: no cover


class PublicationBlockView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationBlockSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationBlock.objects.filter(pk=self.pk,
                                               publication=self.publication)


class PublicationBlockLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPublicationBlockLogs'


class PublicationBlockLogsView(PublicationRelatedObjectLogsView):

    schema = PublicationBlockLogsSchema()

    def get_queryset(self):
        """
        """
        super().get_data()
        item = get_object_or_404(PublicationBlock.objects.select_related('publication'),
                                 pk=self.pk,
                                 publication=self.publication)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(self.pk, content_type_id)
