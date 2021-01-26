from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.publications.models import *
from cms.publications.serializers import *

from rest_framework import filters, generics
from rest_framework.permissions import IsAdminUser

from .. exceptions import LoggedPermissionDenied
from .. pagination import UniCmsApiPagination


class PublicationLocalizationList(generics.ListCreateAPIView):
    """
    """
    description = ""
    serializer_class = PublicationLocalizationSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['is_active', 'created', 'modified']
    search_fields = ['title', 'language', 'subheading', 'content']
    pagination_class = UniCmsApiPagination

    def get_queryset(self):
        """
        """
        pk = self.kwargs['publication_id']
        publication = get_object_or_404(Publication, pk=pk)
        return PublicationLocalization.objects.filter(publication=publication)

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
    serializer_class = PublicationLocalizationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        pk = self.kwargs['pk']
        publication = get_object_or_404(Publication, pk=pub_id)
        return PublicationLocalization.objects.filter(pk=pk,
                                                      publication=publication)

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
