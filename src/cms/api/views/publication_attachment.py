import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

# from cms.api.serializers import PublicationSerializer

from cms.contexts.decorators import detect_language
from cms.contexts.models import WebPath
from cms.contexts import settings as contexts_settings

from cms.publications.models import Publication, PublicationAttachment, PublicationContext
from cms.publications.paginators import Paginator
from cms.publications.serializers import PublicationSerializer, PublicationAttachmentSerializer
from cms.publications.utils import publication_context_base_filter

from rest_framework import filters

from .. pagination import UniCmsApiPagination
from .. permissions import UserCanAddPublicationOrAdminReadonly
from .. utils import check_user_permission_on_object


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


class PublicationAttachmentList(generics.ListCreateAPIView):
    """
    """
    description = ""
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'file', 'descripion']
    pagination_class = UniCmsApiPagination
    permission_classes = [IsAdminUser]
    serializer_class = PublicationAttachmentSerializer

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        items = PublicationAttachment.objects.filter(publication__pk=pub_id)
        is_active = self.request.GET.get('is_active')
        if is_active:
            items = items.filter(is_active=is_active)
        return items

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get publication
            publication = serializer.validated_data.get('publication')
            # check permissions on carousel
            permission = check_user_permission_on_object(request.user,
                                                         publication,
                                                         'cmspublications.change_publications')
            if not permission:
                return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)

            return super().post(request, *args, **kwargs)


class PublicationAttachmentView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PublicationAttachmentSerializer
    error_msg = _("You don't have permissions")

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        pk = self.kwargs['pk']
        attachments = PublicationAttachment.objects.filter(pk=pk,
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
            permission = check_user_permission_on_object(request.user,
                                                         publication,
                                                         'cmspublications.change_publication')
            if not permission:
                return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
            return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            publication = item.publication
            permission = check_user_permission_on_object(request.user,
                                                         publication,
                                                         'cmspublications.change_publication')
            if not permission:
                return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        publication = item.publication
        permission = check_user_permission_on_object(request.user,
                                                     publication,
                                                     'cmspublications.change_publication')
        if not permission:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
