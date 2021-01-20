from django.conf import settings
from django.http import Http404

from cms.contexts import settings as contexts_settings

from cms.medias.models import MediaCollectionItem
from cms.medias.serializers import MediaCollectionItemSerializer

from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from .. exceptions import LoggedPermissionDenied
from .. pagination import UniCmsApiPagination
from .. utils import check_user_permission_on_object


class MediaCollectionItemList(generics.ListCreateAPIView):
    """
    """
    description = ""
    pagination_class = UniCmsApiPagination
    permission_classes = [IsAdminUser]
    serializer_class = MediaCollectionItemSerializer

    def get_queryset(self):
        """
        """
        collection_id = self.kwargs['collection_id']
        items = MediaCollectionItem.objects.filter(collection__pk=collection_id)
        is_active = self.request.GET.get('is_active')
        if is_active:
            items = items.filter(is_active=is_active)
        return items

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get collection
            collection = serializer.validated_data.get('collection')
            # check permissions on carousel
            permission = check_user_permission_on_object(request.user,
                                                         collection,
                                                         'cmscarousels.change_mediacollection')
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class MediaCollectionItemView(generics.RetrieveUpdateDestroyAPIView):
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
        items = MediaCollectionItem.objects.filter(pk=item_id,
                                                   collection__pk=collection_id)
        return items

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        collection = item.collection
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            # check permissions on collection
            permission = check_user_permission_on_object(request.user,
                                                         collection,
                                                         'cmsmedias.change_mediacollection')
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        collection = item.collection
        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            # check permissions on collection
            permission = check_user_permission_on_object(request.user,
                                                         collection,
                                                         'cmsmedias.change_mediacollection')
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
                                                     collection,
                                                     'cmsmedias.change_mediacollection')
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)
