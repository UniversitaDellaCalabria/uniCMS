from django.http import Http404

from rest_framework import filters, generics
from rest_framework.permissions import IsAdminUser


from cms.publications.models import *
from cms.publications.serializers import *

from .. exceptions import LoggedPermissionDenied
from .. pagination import UniCmsApiPagination


class PublicationLocalizationList(generics.ListCreateAPIView):
    """
    """
    description = ""
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'language', 'subheading', 'content']
    pagination_class = UniCmsApiPagination
    permission_classes = [IsAdminUser]
    serializer_class = PublicationLocalizationSerializer

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        items = PublicationLocalization.objects.filter(publication__pk=pub_id)
        return items

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get publication
            publication = serializer.validated_data.get('publication')
            # check permissions on publication
            has_permission = publication.is_localizable_by(request.user)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class PublicationLocalizationView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PublicationLocalizationSerializer

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        pk = self.kwargs['pk']
        localizations = PublicationLocalization.objects.filter(pk=pk,
                                                               publication__pk=pub_id)
        return localizations

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            publication = item.publication
            # check permissions on publication
            has_permission = publication.is_localizable_by(request.user)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            publication = item.publication
            # check permissions on publication
            has_permission = publication.is_localizable_by(request.user)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        publication = item.publication
        # check permissions on publication
        has_permission = publication.is_localizable_by(request.user)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)
