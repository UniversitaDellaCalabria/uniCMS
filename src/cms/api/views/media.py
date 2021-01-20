import os

from django.http import Http404

from rest_framework import generics
from rest_framework import filters
from rest_framework.permissions import IsAdminUser


from cms.medias.models import Media
from cms.medias.serializers import MediaSerializer

from .. exceptions import LoggedPermissionDenied
from .. pagination import UniCmsApiPagination
from .. permissions import UserCanAddMediaOrAdminReadonly
from .. utils import check_user_permission_on_object


class MediaList(generics.ListCreateAPIView):
    """
    """
    description = ""
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'file', 'description']
    pagination_class = UniCmsApiPagination
    permission_classes = [UserCanAddMediaOrAdminReadonly]
    serializer_class = MediaSerializer

    def get_queryset(self):
        items = Media.objects.all()
        is_active = self.request.GET.get('is_active')
        if is_active:
            items = items.filter(is_active=is_active)
        return items


class MediaView(generics.RetrieveUpdateDestroyAPIView):
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
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            permission = check_user_permission_on_object(request.user,
                                                         item,
                                                         'cmsmedias.change_media')
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            permission = check_user_permission_on_object(request.user,
                                                         item,
                                                         'cmsmedias.change_media')
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = check_user_permission_on_object(request.user,
                                                     item,
                                                     'cmsmedias.delete_media')
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        media = self.get_queryset().first()
        os.remove(media.file.path)
        return super().delete(request, *args, **kwargs)
