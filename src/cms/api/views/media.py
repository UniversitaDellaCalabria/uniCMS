import logging
import os

from django.http import Http404

from cms.medias.forms import MediaForm
from cms.medias.models import Media
from cms.medias.serializers import MediaSerializer, MediaSelectOptionsSerializer

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from . generics import UniCMSCachedRetrieveUpdateDestroyAPIView, UniCMSListCreateAPIView, UniCMSListSelectOptionsAPIView
from .. exceptions import LoggedPermissionDenied
from .. permissions import MediaGetCreatePermissions
from .. serializers import UniCMSFormSerializer
from .. utils import check_user_permission_on_object


logger = logging.getLogger(__name__)


class MediaList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['title', 'file', 'description']
    permission_classes = [MediaGetCreatePermissions]
    serializer_class = MediaSerializer
    queryset = Media.objects.all()


class MediaView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MediaSerializer

    def get_queryset(self):
        """
        """
        media_id = self.kwargs['pk']
        medias = Media.objects.filter(pk=media_id)
        return medias

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = check_user_permission_on_object(request.user,
                                                     item)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = check_user_permission_on_object(request.user,
                                                     item)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = check_user_permission_on_object(request.user,
                                                     item, 'delete')
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        media = self.get_queryset().first()
        try:
            os.remove(media.file.path)
        except: # pragma: no cover
            logger.warning(f'File {media.file.path} not found')
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
