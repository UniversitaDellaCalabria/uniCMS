import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.translation import gettext_lazy as _

from rest_framework import generics
from rest_framework import filters
from rest_framework.permissions import IsAdminUser

from cms.carousels.models import *
from cms.carousels.serializers import *

from cms.contexts import settings as contexts_settings

from .. pagination import UniCmsApiPagination
from .. utils import check_user_permission_on_object


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


class CarouselItemLocalizationList(generics.ListCreateAPIView):
    """
    """
    description = ""
    filter_backends = [filters.SearchFilter]
    search_fields = ['language', 'pre_heading', 'heading', 'description']
    pagination_class = UniCmsApiPagination
    permission_classes = [IsAdminUser]
    serializer_class = CarouselItemLocalizationSerializer

    def get_queryset(self):
        """
        """
        carousel_id = self.kwargs['carousel_id']
        carousel_item_id = self.kwargs['carousel_item_id']
        items = CarouselItemLocalization.objects.filter(carousel_item__carousel__pk=carousel_id,
                                                        carousel_item__pk=carousel_item_id)
        is_active = self.request.GET.get('is_active')
        if is_active:
            items = items.filter(is_active=is_active)
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
                raise PermissionDenied()

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
                raise PermissionDenied()
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
                raise PermissionDenied()
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
            raise PermissionDenied()
        return super().delete(request, *args, **kwargs)
