from django.http import Http404

from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from cms.carousels.models import *
from cms.carousels.serializers import *

from . generics import UniCMSListCreateAPIView
from .. exceptions import LoggedPermissionDenied
from .. utils import check_user_permission_on_object


class CarouselItemLocalizationList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['language', 'pre_heading', 'heading', 'description']
    permission_classes = [IsAdminUser]
    serializer_class = CarouselItemLocalizationSerializer

    def get_queryset(self):
        """
        """
        carousel_id = self.kwargs['carousel_id']
        carousel_item_id = self.kwargs['carousel_item_id']
        items = CarouselItemLocalization.objects.filter(carousel_item__carousel__pk=carousel_id,
                                                        carousel_item__pk=carousel_item_id)
        return items

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get carousel item
            carousel_item = serializer.validated_data.get('carousel_item')
            # check permissions on carousel
            permission = check_user_permission_on_object(request.user,
                                                         carousel_item.carousel,
                                                         'cmscarousels.change_carousel')
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class CarouselItemLocalizationView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = CarouselItemLocalizationSerializer

    def get_queryset(self):
        """
        """
        carousel_id = self.kwargs['carousel_id']
        carousel_item_id = self.kwargs['carousel_item_id']
        item_id = self.kwargs['pk']
        items = CarouselItemLocalization.objects.filter(pk=item_id,
                                                        carousel_item__carousel__pk=carousel_id,
                                                        carousel_item__pk=carousel_item_id)
        return items

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        carousel_item = item.carousel_item
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            # check permissions on carousel
            permission = check_user_permission_on_object(request.user,
                                                         carousel_item.carousel,
                                                         'cmscarousels.change_carousel')
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        carousel_item = item.carousel_item
        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            # check permissions on carousel
            permission = check_user_permission_on_object(request.user,
                                                         carousel_item.carousel,
                                                         'cmscarousels.change_carousel')
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        carousel_item = item.carousel_item
        # check permissions on carousel
        permission = check_user_permission_on_object(request.user,
                                                     carousel_item.carousel,
                                                     'cmscarousels.change_carousel')
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)
