import logging
import os

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.medias import settings as media_settings
from cms.medias.forms import MediaForm
from cms.medias.models import Media
from cms.medias.serializers import MediaSerializer, MediaSelectOptionsSerializer
from cms.templates.utils import secure_url

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from cms.medias.utils import _remove_file

from . generics import UniCMSCachedRetrieveUpdateDestroyAPIView, UniCMSListCreateAPIView, UniCMSListSelectOptionsAPIView
from . logs import ObjectLogEntriesList
from .. exceptions import LoggedPermissionDenied
from .. permissions import MediaGetCreatePermissions
from .. serializers import UniCMSFormSerializer
from .. utils import check_user_permission_on_object


logger = logging.getLogger(__name__)

FILETYPE_ALLOWED = getattr(settings, 'FILETYPE_ALLOWED',
                           media_settings.FILETYPE_ALLOWED)


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
        if 'file' in request.data:
            _remove_file(item)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_object()
        permission = check_user_permission_on_object(request.user,
                                                     item)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        _remove_file(item)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        permission = check_user_permission_on_object(request.user,
                                                     item, 'delete')
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        _remove_file(item)
        return super().delete(request, *args, **kwargs)


class MediaFormView(APIView):

    def get(self, *args, **kwargs):
        form = MediaForm()
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class EditorialBoardMediaOptionListSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
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
    def get_operation_id(self, path, method):# pragma: no cover
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
