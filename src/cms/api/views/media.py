import logging
import os

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.medias.filetypes import FILETYPE_ALLOWED
from cms.medias.forms import MediaForm
from cms.medias.models import Media
from cms.medias.serializers import MediaSerializer, MediaSelectOptionsSerializer
from cms.templates.utils import secure_url

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from . generics import UniCMSCachedRetrieveUpdateDestroyAPIView, UniCMSListCreateAPIView, UniCMSListSelectOptionsAPIView, UniCMSFormView
from . logs import ObjectLogEntriesList
from .. exceptions import LoggedPermissionDenied
from .. permissions import MediaGetCreatePermissions
from .. serializers import UniCMSFormSerializer
from .. utils import check_user_permission_on_object


logger = logging.getLogger(__name__)


class MediaList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['title', 'file', 'description', 'file_type', 'uuid']
    permission_classes = [MediaGetCreatePermissions]
    filterset_fields = ['created', 'modified', 'created_by', 'file_type']
    serializer_class = MediaSerializer
    queryset = Media.objects.all()


class MediaView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MediaSerializer

    def get_object(self):
        media_id = self.kwargs['pk']
        return get_object_or_404(Media, pk=media_id)

    def patch(self, request, *args, **kwargs):
        item = self.get_object()
        permission = check_user_permission_on_object(request.user,
                                                     item)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        response = super().patch(request, *args, **kwargs)
        cache.delete(f'media-{item.uuid}')
        return response

    def put(self, request, *args, **kwargs):
        item = self.get_object()
        permission = check_user_permission_on_object(request.user,
                                                     item)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        response = super().put(request, *args, **kwargs)
        cache.delete(f'media-{item.uuid}')
        return response

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        permission = check_user_permission_on_object(request.user,
                                                     item, 'delete')
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        response = super().delete(request, *args, **kwargs)
        cache.delete(f'media-{item.uuid}')
        return response


class MediaFormView(UniCMSFormView):

    def get(self, *args, **kwargs):
        form = MediaForm()
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class EditorialBoardMediaOptionListSchema(AutoSchema):
    def get_operation_id(self, path, method):
        return 'listMediaSelectOptions'


class MediaOptionList(UniCMSListSelectOptionsAPIView):
    """
    """
    description = ""
    search_fields = ['title']
    serializer_class = MediaSelectOptionsSerializer
    filterset_fields = ['file_type']
    queryset = Media.objects.all()
    schema = EditorialBoardMediaOptionListSchema()


class MediaOptionView(generics.RetrieveAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MediaSelectOptionsSerializer

    def get_queryset(self):
        """
        """
        media_id = self.kwargs['pk']
        media = Media.objects.filter(pk=media_id)
        return media


class MediaLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):
        return 'listMediaLogs'


class MediaLogsView(ObjectLogEntriesList):

    schema = MediaLogsSchema()

    def get_queryset(self, **kwargs):
        """
        """
        object_id = self.kwargs['pk']
        item = get_object_or_404(Media, pk=object_id)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(object_id, content_type_id)


class MediaFileTypeAllowedList(APIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        """
        return Response(tuple(sorted(FILETYPE_ALLOWED)))
