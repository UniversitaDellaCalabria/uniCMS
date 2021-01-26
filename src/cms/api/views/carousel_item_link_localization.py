from django.http import Http404

from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from cms.carousels.models import *
from cms.carousels.serializers import *

from . generics import UniCMSListCreateAPIView
from .. exceptions import LoggedPermissionDenied
from .. utils import check_user_permission_on_object


class CarouselItemLinkLocalizationList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['language', 'title']
    serializer_class = CarouselItemLinkLocalizationSerializer

    def get_queryset(self):
        """
        """
        carousel_id = self.kwargs['carousel_id']
        carousel_item_id = self.kwargs['carousel_item_id']
        carousel_item_link_id = self.kwargs['carousel_item_link_id']
        items = CarouselItemLinkLocalization.objects.filter(carousel_item_link__pk=carousel_item_link_id,
                                                            carousel_item_link__carousel_item__pk=carousel_item_id,
                                                            carousel_item_link__carousel_item__carousel__pk=carousel_id)
        return items

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get carousel item
            carousel_item_link = serializer.validated_data.get('carousel_item_link')
            # check permissions on carousel
            carousel = carousel_item_link.carousel_item.carousel
            permission = check_user_permission_on_object(request.user,
                                                         carousel,
                                                         'cmscarousels.change_carousel')
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class CarouselItemLinkLocalizationView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = CarouselItemLinkLocalizationSerializer

    def get_queryset(self):
        """
        """
        carousel_id = self.kwargs['carousel_id']
        carousel_item_id = self.kwargs['carousel_item_id']
        carousel_item_link_id = self.kwargs['carousel_item_link_id']
        item_id = self.kwargs['pk']
        items = CarouselItemLinkLocalization.objects.filter(pk=item_id,
                                                            carousel_item_link__pk=carousel_item_link_id,
                                                            carousel_item_link__carousel_item__pk=carousel_item_id,
                                                            carousel_item_link__carousel_item__carousel__pk=carousel_id)
        return items

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        carousel_item_link = item.carousel_item_link
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            # check permissions on carousel
            carousel = carousel_item_link.carousel_item.carousel
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
        carousel_item_link = item.carousel_item_link
        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            # check permissions on carousel
            carousel = carousel_item_link.carousel_item.carousel
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
        carousel_item_link = item.carousel_item_link
        # check permissions on carousel
        carousel = carousel_item_link.carousel_item.carousel
        permission = check_user_permission_on_object(request.user,
                                                     carousel,
                                                     'cmscarousels.change_carousel')
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)
