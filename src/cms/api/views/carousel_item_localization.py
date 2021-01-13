import logging

# from django.contrib.auth.decorators import login_required
# from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from cms.api.serializers import settings

from cms.carousels.models import *
from cms.carousels.serializers import *

from cms.contexts import settings as contexts_settings



from .. pagination import UniCmsApiPagination
from .. permissions import (UserCanAddCarouselOrAdminReadonly,
                            UserCanAddMediaOrAdminReadonly)
from .. utils import check_user_permission_on_object


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


class CarouselItemLocalizationList(generics.ListCreateAPIView):
    """
    """
    description = ""
    pagination_class = UniCmsApiPagination
    permission_classes = [IsAdminUser]
    serializer_class = CarouselItemLocalizationSerializer
    error_msg = _("You don't have permissions")

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
        carousel_id = kwargs['carousel_id']
        carousel_item_id = kwargs['carousel_item_id']
        # can edit carousel defined in URL
        if int(request.data['carousel_item']) != carousel_item_id:
            error_msg = _("Carousel Item ID must be {}").format(carousel_item_id)
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)
        # get carousel item
        carousel_item = get_object_or_404(CarouselItem,
                                          pk=carousel_item_id,
                                          carousel__pk=carousel_id)
        # check permissions on carousel
        permission = check_user_permission_on_object(request.user,
                                                     carousel_item.carousel,
                                                     'cmscarousels.change_carousel')
        if not permission:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)

        return super().post(request, *args, **kwargs)


class CarouselItemLocalizationView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = CarouselItemLocalizationSerializer
    error_msg = _("You don't have permissions")

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
        carousel_id = kwargs['carousel_id']
        carousel_item_id = self.kwargs['carousel_item_id']
        # can edit carousel defined in URL
        if request.data.get('carousel_item') and int(request.data['carousel_item']) != carousel_item_id:
            error_msg = _("Carousel item ID must be {}").format(carousel_item_id)
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)
        # get carousel item
        carousel_item = get_object_or_404(CarouselItem,
                                          pk=carousel_item_id,
                                          carousel__pk=carousel_id)
        # check permissions on carousel
        permission = check_user_permission_on_object(request.user,
                                                     carousel_item.carousel,
                                                     'cmscarousels.change_carousel')
        if not permission:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        carousel_id = kwargs['carousel_id']
        carousel_item_id = self.kwargs['carousel_item_id']
        # can edit carousel defined in URL
        if int(request.data['carousel_item']) != carousel_item_id:
            error_msg = _("Carousel item ID must be {}").format(carousel_item_id)
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)
        # get carousel item
        carousel_item = get_object_or_404(CarouselItem,
                                          pk=carousel_item_id,
                                          carousel__pk=carousel_id)
        # check permissions on carousel
        permission = check_user_permission_on_object(request.user,
                                                     carousel_item.carousel,
                                                     'cmscarousels.change_carousel')
        if not permission:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # get carousel
        carousel_id = kwargs['carousel_id']
        carousel_item_id = self.kwargs['carousel_item_id']
        # get carousel item
        carousel_item = get_object_or_404(CarouselItem,
                                          pk=carousel_item_id,
                                          carousel__pk=carousel_id)
        # check permissions on carousel
        permission = check_user_permission_on_object(request.user,
                                                     carousel_item.carousel,
                                                     'cmscarousels.change_carousel')
        if not permission:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
