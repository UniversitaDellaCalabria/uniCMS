from django.http import Http404


from cms.medias.models import MediaCollection
from cms.medias.serializers import MediaCollectionSerializer

from rest_framework import filters, generics
from rest_framework.permissions import IsAdminUser

from .. exceptions import LoggedPermissionDenied
from .. pagination import UniCmsApiPagination
from .. permissions import UserCanAddMediaCollectionOrAdminReadonly
from .. utils import check_user_permission_on_object


class MediaCollectionList(generics.ListCreateAPIView):
    """
    """
    description = ""
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'tags__name']
    pagination_class = UniCmsApiPagination
    permission_classes = [UserCanAddMediaCollectionOrAdminReadonly]
    serializer_class = MediaCollectionSerializer
    items = MediaCollection.objects.all()

    # def get_queryset(self):
        # items = MediaCollection.objects.all()
        # is_active = self.request.GET.get('is_active')
        # if is_active:
            # items = items.filter(is_active=is_active)
        # return items


class MediaCollectionView(generics.RetrieveUpdateDestroyAPIView):
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
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            permission = check_user_permission_on_object(request.user,
                                                         item,
                                                         'cmsmedias.change_mediacollection')
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
                                                         'cmsmedias.change_mediacollection')
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = check_user_permission_on_object(request.user,
                                                     item,
                                                     'cmsmedias.delete_mediacollection')
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)
