from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.carousels.forms import CarouselItemLocalizationForm
from cms.carousels.models import *
from cms.carousels.serializers import *

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from . generics import *
from . logs import ObjectLogEntriesList
from .. exceptions import LoggedPermissionDenied
from .. serializers import UniCMSFormSerializer
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
        carousel_id = self.kwargs.get('carousel_id')
        carousel_item_id = self.kwargs.get('carousel_item_id')
        if carousel_id and carousel_item_id:
            return CarouselItemLocalization.objects.filter(carousel_item__carousel__pk=carousel_id,
                                                           carousel_item__pk=carousel_item_id)
        return CarouselItemLocalization.objects.none() # pragma: no cover

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get carousel item
            carousel_item = serializer.validated_data.get('carousel_item')
            # check permissions on carousel
            permission = check_user_permission_on_object(request.user,
                                                         carousel_item.carousel)
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class CarouselItemLocalizationView(UniCMSCachedRetrieveUpdateDestroyAPIView):
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
        items = CarouselItemLocalization.objects\
                                        .select_related('carousel_item')\
                                        .filter(pk=item_id,
                                                carousel_item__carousel__pk=carousel_id,
                                                carousel_item__pk=carousel_item_id)
        return items

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        carousel_item = item.carousel_item
        # check permissions on carousel
        permission = check_user_permission_on_object(request.user,
                                                     carousel_item.carousel)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        carousel_item = item.carousel_item
        # check permissions on carousel
        permission = check_user_permission_on_object(request.user,
                                                     carousel_item.carousel)
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
                                                     carousel_item.carousel)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class CarouselItemLocalizationFormView(APIView):

    def get(self, *args, **kwargs):
        form = CarouselItemLocalizationForm(carousel_item_id=kwargs.get('carousel_item_id'),
                                            carousel_id=kwargs.get('carousel_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class CarouselItemLocalizationLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listCarouselItemLocalizationLogs'


class CarouselItemLocalizationLogsView(ObjectLogEntriesList):

    schema = CarouselItemLocalizationLogsSchema()

    def get_queryset(self, **kwargs):
        """
        """
        carousel_id = self.kwargs['carousel_id']
        carousel_item_id = self.kwargs['carousel_item_id']
        object_id = self.kwargs['pk']
        item = get_object_or_404(CarouselItemLocalization.objects.select_related('carousel_item'),
                                 pk=object_id,
                                 carousel_item__carousel__pk=carousel_id,
                                 carousel_item__pk=carousel_item_id)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(object_id, content_type_id)
