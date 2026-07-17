import logging
import os

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.publications.forms import PublicationAttachmentForm
from cms.publications.models import Publication, PublicationAttachment
from cms.publications.serializers import PublicationAttachmentSerializer

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from . generics import UniCMSCachedRetrieveUpdateDestroyAPIView

from .. exceptions import LoggedPermissionDenied
from .. serializers import UniCMSFormSerializer
from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList, PublicationRelatedObjectLogsView


logger = logging.getLogger(__name__)


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


class PublicationAttachmentView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    serializer_class = PublicationAttachmentSerializer
    permission_classes = [IsAdminUser]

    def get_object(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        self.pk = self.kwargs['pk']
        self.publication = get_object_or_404(Publication, pk=pub_id)
        return get_object_or_404(PublicationAttachment,
                                 pk=self.pk,
                                 publication=self.publication)
    
    def patch(self, request, *args, **kwargs):
        item = self.get_object()
        has_permission = self.publication.is_editable_by(request.user)
        
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)

        if 'file' in request.data:
            try:
                os.remove(item.file.path)
            except Exception: # pragma: no cover
                logger.warning(f'Publication attachment {item.file.path} not found')
            
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_object()
        has_permission = self.publication.is_editable_by(request.user)
        
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)

        if 'file' in request.data:
            try:
                os.remove(item.file.path)
            except Exception: # pragma: no cover
                logger.warning(f'Publication attachment {item.file.path} not found')
            
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        has_permission = self.publication.is_editable_by(request.user)
        
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)

        try:
            os.remove(item.file.path)
        except Exception: # pragma: no cover
            logger.warning(f'Publication attachment {item.file.path} not found')
            
        return super().delete(request, *args, **kwargs)


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
