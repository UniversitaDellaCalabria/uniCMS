from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.publications.forms import PublicationLocalizationForm
from cms.publications.models import *
from cms.publications.serializers import *

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from . generics import *

from .. exceptions import LoggedPermissionDenied
from .. serializers import UniCMSFormSerializer


class PublicationLocalizationList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    serializer_class = PublicationLocalizationSerializer
    filterset_fields = ['is_active', 'created', 'modified']
    search_fields = ['title', 'language', 'subheading', 'content']

    def get_queryset(self):
        """
        """
        pk = self.kwargs.get('publication_id')
        if pk:
            publication = get_object_or_404(Publication, pk=pk)
            return PublicationLocalization.objects.filter(publication=publication)
        return PublicationLocalization.objects.none() # pragma: no cover

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


class PublicationLocalizationView(UniCMSCachedRetrieveUpdateDestroyAPIView):
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
        return PublicationLocalization.objects\
                                      .select_related('publication')\
                                      .filter(pk=pk,
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


class PublicationLocalizationFormView(APIView):

    def get(self, *args, **kwargs):
        form = PublicationLocalizationForm(publication_id=kwargs.get('publication_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
