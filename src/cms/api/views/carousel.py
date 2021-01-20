from django.http import Http404

from rest_framework import generics
from rest_framework import filters
from rest_framework.permissions import IsAdminUser

from cms.carousels.models import *
from cms.carousels.serializers import *


from .. exceptions import LoggedPermissionDenied
from .. pagination import UniCmsApiPagination
from .. permissions import UserCanAddCarouselOrAdminReadonly
from .. utils import check_user_permission_on_object


class CarouselList(generics.ListCreateAPIView):
    """
    """
    description = ""
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    pagination_class = UniCmsApiPagination
    permission_classes = [UserCanAddCarouselOrAdminReadonly]
    serializer_class = CarouselSerializer
    queryset = Carousel.objects.all()


class CarouselView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = CarouselSerializer

    def get_queryset(self):
        """
        """
        carousel_id = self.kwargs['pk']
        carousels = Carousel.objects.filter(pk=carousel_id)
        return carousels

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            permission = check_user_permission_on_object(request.user,
                                                         item,
                                                         'cmscarousels.change_carousel')
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
                                                         'cmscarousels.change_carousel')
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = check_user_permission_on_object(request.user,
                                                     item,
                                                     'cmscarousels.delete_carousel')
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)
