from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.medias.forms import MediaCollectionForm
from cms.medias.models import MediaCollection
from cms.medias.serializers import MediaCollectionSerializer, MediaCollectionSelectOptionsSerializer

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from . generics import UniCMSCachedRetrieveUpdateDestroyAPIView, UniCMSListCreateAPIView, UniCMSListSelectOptionsAPIView
from . logs import ObjectLogEntriesList
from .. exceptions import LoggedPermissionDenied
from .. permissions import MediaCollectionGetCreatePermissions
from .. serializers import UniCMSFormSerializer
from .. utils import check_user_permission_on_object


class MediaCollectionList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    permission_classes = [MediaCollectionGetCreatePermissions]
    serializer_class = MediaCollectionSerializer
    queryset = MediaCollection.objects.all()
    search_fields = ['name', 'description', 'tags__name']


class MediaCollectionView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MediaCollectionSerializer

    def get_queryset(self):
        """
        """
        media_collection_id = self.kwargs['pk']
        items = MediaCollection.objects.filter(pk=media_collection_id)
        return items

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
        return super().delete(request, *args, **kwargs)


class MediaCollectionFormView(APIView):

    def get(self, *args, **kwargs):
        form = MediaCollectionForm()
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class EditorialBoardMediaCollectionOptionListSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listMediaCollectionSelectOptions'


class MediaCollectionOptionList(UniCMSListSelectOptionsAPIView):
    """
    """
    description = ""
    search_fields = ['name']
    serializer_class = MediaCollectionSelectOptionsSerializer
    queryset = MediaCollection.objects.all()
    schema = EditorialBoardMediaCollectionOptionListSchema()


class MediaCollectionOptionView(generics.RetrieveAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MediaCollectionSelectOptionsSerializer

    def get_queryset(self):
        """
        """
        collection_id = self.kwargs['pk']
        collection = MediaCollection.objects.filter(pk=collection_id)
        return collection


class MediaCollectionLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listMediaCollectionLogs'


class MediaCollectionLogsView(ObjectLogEntriesList):

    schema = MediaCollectionLogsSchema()

    def get_queryset(self, **kwargs):
        """
        """
        object_id = self.kwargs['pk']
        item = get_object_or_404(MediaCollection, pk=object_id)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(object_id, content_type_id)
