import logging

# from django.contrib.auth.decorators import login_required
# from django.contrib.admin.views.decorators import staff_member_required
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


class CarouselList(generics.ListCreateAPIView):
    """
    """
    description = ""
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
    error_msg = _("You don't have permissions")

    def get_queryset(self):
        """
        """
        carousel_id = self.kwargs['pk']
        carousels = Carousel.objects.filter(pk=carousel_id)
        return carousels

    def patch(self, request, *args, **kwargs):
        permission = check_user_permission_on_object(request.user,
                                                     self.get_queryset().first(),
                                                     'cmscarousels.change_carousel')
        if not permission:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        permission = check_user_permission_on_object(request.user,
                                                     self.get_queryset().first(),
                                                     'cmscarousels.change_carousel')
        if not permission:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        permission = check_user_permission_on_object(request.user,
                                                     self.get_queryset().first(),
                                                     'cmscarousels.delete_carousel')
        if not permission:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
