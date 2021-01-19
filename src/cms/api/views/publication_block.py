import logging

from django.conf import settings
from django.http import Http404
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

# from cms.api.serializers import PublicationSerializer

from cms.contexts import settings as contexts_settings

from cms.publications.models import *
from cms.publications.serializers import *

from rest_framework import filters

from .. pagination import UniCmsApiPagination


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


class PublicationBlockList(generics.ListCreateAPIView):
    """
    """
    description = ""
    filter_backends = [filters.SearchFilter]
    search_fields = ['block__name']
    pagination_class = UniCmsApiPagination
    permission_classes = [IsAdminUser]
    serializer_class = PublicationBlockSerializer
    error_msg = _("You don't have permissions")

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        items = PublicationBlock.objects.filter(publication__pk=pub_id)
        return items

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get publication
            publication = serializer.validated_data.get('publication')
            # check permissions on publication
            has_permission = publication.is_editable_by(request.user)
            if not has_permission:
                return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)

            return super().post(request, *args, **kwargs)


class PublicationBlockView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PublicationBlockSerializer
    error_msg = _("You don't have permissions")

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        pk = self.kwargs['pk']
        attachments = PublicationBlock.objects.filter(pk=pk,
                                                      publication__pk=pub_id)
        return attachments

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            publication = item.publication
            # check permissions on publication
            has_permission = publication.is_editable_by(request.user)
            if not has_permission:
                return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
            return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            publication = item.publication
            # check permissions on publication
            has_permission = publication.is_editable_by(request.user)
            if not has_permission:
                return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        publication = item.publication
        # check permissions on publication
        has_permission = publication.is_editable_by(request.user)
        if not has_permission:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
