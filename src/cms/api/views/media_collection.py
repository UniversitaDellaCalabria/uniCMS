from django.http import Http404

from cms.medias.forms import MediaCollectionForm
from cms.medias.models import MediaCollection
from cms.medias.serializers import MediaCollectionSerializer

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from . generics import UniCMSCachedRetrieveUpdateDestroyAPIView, UniCMSListCreateAPIView
from .. exceptions import LoggedPermissionDenied
from .. permissions import MediaCollectionGetCreatePermissions
from .. serializers import UniCMSFormSerializer
from .. utils import check_user_permission_on_object


class MediaCollectionList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    permission_classes = [MediaCollectionGetCreatePermissions]
    serializer_class = MediaCollectionSerializer
    queryset = MediaCollection.objects.all()
    search_fields = ['name', 'description', 'tags__name']


class MediaCollectionView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MediaCollectionSerializer

    def get_queryset(self):
        """
        """
        media_collection_id = self.kwargs['pk']
        items = MediaCollection.objects.filter(pk=media_collection_id)
        return items

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


class MediaCollectionFormView(APIView):

    def get(self, *args, **kwargs):
        form = MediaCollectionForm()
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
