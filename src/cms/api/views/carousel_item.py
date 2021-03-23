from django.http import Http404

from cms.carousels.forms import CarouselItemForm
from cms.carousels.models import *
from cms.carousels.serializers import *

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from . generics import *
from .. exceptions import LoggedPermissionDenied
from .. serializers import UniCMSFormSerializer
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
        carousel_id = self.kwargs.get('carousel_id')
        if carousel_id:
            return CarouselItem.objects.filter(carousel__pk=carousel_id)
        return CarouselItem.objects.none() # pragma: no cover

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get carousel
            carousel = serializer.validated_data.get('carousel')
            # check permissions on carousel
            permission = check_user_permission_on_object(request.user,
                                                         carousel)
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)

            return super().post(request, *args, **kwargs)


class CarouselItemView(UniCMSCachedRetrieveUpdateDestroyAPIView):
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
        items = CarouselItem.objects\
                            .select_related('carousel')\
                            .filter(pk=item_id, carousel__pk=carousel_id)
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
                                                         carousel)
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
                                                         carousel)
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
                                                     carousel)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class CarouselItemFormView(APIView):

    def get(self, *args, **kwargs):
        form = CarouselItemForm(carousel_id=kwargs.get('carousel_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class CarouselItemGenericFormView(APIView):

    def get(self, *args, **kwargs):
        form = CarouselItemForm()
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
