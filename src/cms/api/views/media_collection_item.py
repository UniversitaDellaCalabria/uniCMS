from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.medias.forms import MediaCollectionItemForm
from cms.medias.models import MediaCollectionItem
from cms.medias.serializers import MediaCollectionItemSerializer

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from . generics import UniCMSCachedRetrieveUpdateDestroyAPIView, UniCMSListCreateAPIView
from . logs import ObjectLogEntriesList
from .. exceptions import LoggedPermissionDenied
from .. serializers import UniCMSFormSerializer
from .. utils import check_user_permission_on_object


class MediaCollectionItemList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    serializer_class = MediaCollectionItemSerializer
    search_fields = ['media__title', 'media__file', 'media__description',
                     'collection__name']

    def get_queryset(self):
        """
        """
        collection_id = self.kwargs.get('collection_id')
        if collection_id:
            return MediaCollectionItem.objects.filter(collection__pk=collection_id)
        return MediaCollectionItem.objects.none() # pragma: no cover

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get collection
            collection = serializer.validated_data.get('collection')
            # check permissions on carousel
            permission = check_user_permission_on_object(request.user,
                                                         collection)
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class MediaCollectionItemView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MediaCollectionItemSerializer

    def get_queryset(self):
        """
        """
        collection_id = self.kwargs['collection_id']
        item_id = self.kwargs['pk']
        items = MediaCollectionItem.objects\
            .select_related('collection')\
            .filter(pk=item_id,
                    collection__pk=collection_id)
        return items

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        collection = item.collection
        # check permissions on collection
        permission = check_user_permission_on_object(request.user,
                                                     collection)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        collection = item.collection
        # check permissions on collection
        permission = check_user_permission_on_object(request.user,
                                                     collection)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        collection = item.collection
        # check permissions on carousel
        permission = check_user_permission_on_object(request.user,
                                                     collection)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class MediaCollectionItemFormView(APIView):

    def get(self, *args, **kwargs):
        form = MediaCollectionItemForm(collection_id=kwargs.get('collection_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class MediaCollectionItemLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listMediaCollectionItemLogs'


class MediaCollectionItemLogsView(ObjectLogEntriesList):

    schema = MediaCollectionItemLogsSchema()

    def get_queryset(self, **kwargs):
        """
        """
        collection_id = self.kwargs['collection_id']
        object_id = self.kwargs['pk']
        item = get_object_or_404(MediaCollectionItem.objects.select_related('collection'),
                                 pk=object_id,
                                 collection__pk=collection_id)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(object_id, content_type_id)
