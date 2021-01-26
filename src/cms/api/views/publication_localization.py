from django.http import Http404

from cms.publications.models import *
from cms.publications.serializers import *

from .. exceptions import LoggedPermissionDenied
from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList


class PublicationLocalizationList(PublicationRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['title', 'language', 'subheading', 'content']
    serializer_class = PublicationLocalizationSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationLocalization.objects.filter(publication=self.publication)

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


class PublicationLocalizationView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationLocalizationSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationLocalization.objects.filter(pk=self.pk,
                                                      publication=self.publication)

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
