from django.http import Http404

from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from cms.carousels.models import *
from cms.carousels.serializers import *

from . generics import UniCMSListCreateAPIView
from .. exceptions import LoggedPermissionDenied
from .. utils import check_user_permission_on_object


class CarouselItemList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['pre_heading', 'heading', 'description']
    serializer_class = CarouselItemSerializer

    def get_queryset(self):
        """
        """
        carousel_id = self.kwargs['carousel_id']
        return CarouselItem.objects.filter(carousel__pk=carousel_id)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get carousel
            carousel = serializer.validated_data.get('carousel')
            # check permissions on carousel
            permission = check_user_permission_on_object(request.user,
                                                         carousel,
                                                         'cmscarousels.change_carousel')
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)

            return super().post(request, *args, **kwargs)


class CarouselItemView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = CarouselItemSerializer

    def get_queryset(self):
        """
        """
        carousel_id = self.kwargs['carousel_id']
        item_id = self.kwargs['pk']
        items = CarouselItem.objects.filter(pk=item_id,
                                            carousel__pk=carousel_id)
        return items

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        carousel = item.carousel
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            new_carousel = serializer.validated_data.get('carousel')
            # check permissions on carousel
            if new_carousel:
                carousel = new_carousel
            permission = check_user_permission_on_object(request.user,
                                                         carousel,
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
            # get carousel
            carousel = serializer.validated_data.get('carousel')
            # check permissions on carousel
            permission = check_user_permission_on_object(request.user,
                                                         carousel,
                                                         'cmscarousels.change_carousel')
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        # get carousel
        carousel = item.carousel
        # check permissions on carousel
        permission = check_user_permission_on_object(request.user,
                                                     carousel,
                                                     'cmscarousels.change_carousel')
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)
