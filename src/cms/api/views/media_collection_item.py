import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.translation import gettext_lazy as _

from cms.contexts import settings as contexts_settings

from cms.medias.models import MediaCollectionItem
from cms.medias.serializers import MediaCollectionItemSerializer

from rest_framework import generics
# from rest_framework import filters
from rest_framework.permissions import IsAdminUser

from .. pagination import UniCmsApiPagination
from .. utils import check_user_permission_on_object


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


class MediaCollectionItemList(generics.ListCreateAPIView):
    """
    """
    description = ""
    pagination_class = UniCmsApiPagination
    permission_classes = [IsAdminUser]
    serializer_class = MediaCollectionItemSerializer
    error_msg = _("You don't have permissions")

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
                raise PermissionDenied()
            return super().post(request, *args, **kwargs)


class MediaCollectionItemView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MediaCollectionItemSerializer
    error_msg = _("You don't have permissions")

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
                raise PermissionDenied()
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
                raise PermissionDenied()
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
            raise PermissionDenied()
        return super().delete(request, *args, **kwargs)
