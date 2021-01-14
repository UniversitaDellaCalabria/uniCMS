import logging

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from cms.contexts import settings as contexts_settings

from cms.medias.models import MediaCollection
from cms.medias.serializers import MediaCollectionSerializer

from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .. pagination import UniCmsApiPagination
from .. permissions import UserCanAddMediaCollectionOrAdminReadonly
from .. utils import check_user_permission_on_object


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


class MediaCollectionList(generics.ListCreateAPIView):
    """
    """
    description = ""
    pagination_class = UniCmsApiPagination
    permission_classes = [UserCanAddMediaCollectionOrAdminReadonly]
    serializer_class = MediaCollectionSerializer

    def get_queryset(self):
        items = MediaCollection.objects.all()
        is_active = self.request.GET.get('is_active')
        if is_active:
            items = items.filter(is_active=is_active)
        return items


class MediaCollectionView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MediaCollectionSerializer
    error_msg = _("You don't have permissions")

    def get_queryset(self):
        """
        """
        media_collection_id = self.kwargs['pk']
        items = MediaCollection.objects.filter(pk=media_collection_id)
        return items

    def patch(self, request, *args, **kwargs):
        permission = check_user_permission_on_object(request.user,
                                                     self.get_queryset().first(),
                                                     'cmsmedias.change_mediacollection')
        if not permission:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        permission = check_user_permission_on_object(request.user,
                                                     self.get_queryset().first(),
                                                     'cmsmedias.change_mediacollection')
        if not permission:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        permission = check_user_permission_on_object(request.user,
                                                     self.get_queryset().first(),
                                                     'cmsmedias.delete_mediacollection')
        if not permission:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)