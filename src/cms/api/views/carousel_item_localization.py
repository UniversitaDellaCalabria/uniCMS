from django.http import Http404

from cms.carousels.forms import CarouselItemLocalizationForm
from cms.carousels.models import *
from cms.carousels.serializers import *

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from . generics import *
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
