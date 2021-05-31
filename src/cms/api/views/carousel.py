from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.carousels.forms import CarouselForm
from cms.carousels.models import *
from cms.carousels.serializers import *

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from . generics import *
from . logs import ObjectLogEntriesList
from .. exceptions import LoggedPermissionDenied
from .. permissions import CarouselGetCreatePermissions
from .. serializers import UniCMSFormSerializer
from .. utils import check_user_permission_on_object


class CarouselList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['name', 'description']
    permission_classes = [CarouselGetCreatePermissions]
    serializer_class = CarouselSerializer
    queryset = Carousel.objects.all()


class CarouselView(UniCMSCachedRetrieveUpdateDestroyAPIView):
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
        permission = check_user_permission_on_object(request.user,
                                                     item)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = check_user_permission_on_object(request.user,
                                                     item)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = check_user_permission_on_object(request.user,
                                                     item, 'delete')
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class CarouselFormView(APIView):

    def get(self, *args, **kwargs):
        form = CarouselForm()
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class CarouselLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listCarouselLogs'


class CarouselLogsView(ObjectLogEntriesList):

    schema = CarouselLogsSchema()

    def get_queryset(self, **kwargs):
        """
        """
        object_id = self.kwargs['pk']
        item = get_object_or_404(Carousel, pk=object_id)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(object_id, content_type_id)


class EditorialBoardCarouselOptionListSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listCarouselSelectOptions'


class CarouselOptionList(UniCMSListSelectOptionsAPIView):
    """
    """
    description = ""
    search_fields = ['name']
    serializer_class = CarouselSelectOptionsSerializer
    queryset = Carousel.objects.all()
    schema = EditorialBoardCarouselOptionListSchema()


class CarouselOptionView(generics.RetrieveAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = CarouselSelectOptionsSerializer

    def get_queryset(self):
        """
        """
        carousel_id = self.kwargs['pk']
        carousel = Carousel.objects.filter(pk=carousel_id)
        return carousel
