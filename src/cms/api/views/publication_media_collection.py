from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.publications.forms import PublicationMediaCollectionForm
from cms.publications.models import *
from cms.publications.serializers import *

from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList, PublicationRelatedObjectLogsView


class PublicationMediaCollectionList(PublicationRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['collection__name', 'collection__description']
    ordering_fields = ['id', 'collection__name',
                       'collection__description', 'order', 'is_active']
    serializer_class = PublicationMediaCollectionSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.publication:
            return PublicationMediaCollection.objects.filter(publication=self.publication)
        return PublicationMediaCollection.objects.none() # pragma: no cover


class PublicationMediaCollectionView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationMediaCollectionSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationMediaCollection.objects.filter(pk=self.pk,
                                                         publication=self.publication)


class PublicationMediaCollectionFormView(APIView):

    def get(self, *args, **kwargs):
        form = PublicationMediaCollectionForm(publication_id=kwargs.get('publication_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PublicationMediaCollectionLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPublicationMediaCollectionLogs'


class PublicationMediaCollectionLogsView(PublicationRelatedObjectLogsView):

    schema = PublicationMediaCollectionLogsSchema()

    def get_queryset(self):
        """
        """
        super().get_data()
        item = get_object_or_404(PublicationMediaCollection.objects.select_related('publication'),
                                 pk=self.pk,
                                 publication=self.publication)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(self.pk, content_type_id)
