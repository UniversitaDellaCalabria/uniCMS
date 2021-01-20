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
from .. permissions import UserCanAddCarouselOrAdminReadonly
from .. utils import check_user_permission_on_object


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


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
                raise PermissionDenied()
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
                raise PermissionDenied()
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = check_user_permission_on_object(request.user,
                                                     item,
                                                     'cmscarousels.delete_carousel')
        if not permission['granted']:
            raise PermissionDenied()
        return super().delete(request, *args, **kwargs)
