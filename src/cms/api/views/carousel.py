from django.http import Http404

from cms.carousels.forms import CarouselForm
from cms.carousels.models import *
from cms.carousels.serializers import *

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from . generics import *
from . locks import ObjectUserLocksList, ObjectUserLocksView

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
