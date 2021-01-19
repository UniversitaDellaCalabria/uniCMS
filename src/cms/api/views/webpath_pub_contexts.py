import logging

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, status
from rest_framework import filters
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from cms.contexts import settings as contexts_settings
from cms.contexts.models import EditorialBoardEditors, WebPath, WebSite
from cms.contexts.utils import is_publisher

from cms.publications.models import PublicationContext
from cms.publications.serializers import PublicationContextSerializer
from cms.contexts.utils import is_publisher

from .. pagination import UniCmsApiPagination


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


class EditorWebpathPublicationContextList(generics.ListCreateAPIView):
    """
    """
    description = ""
    filter_backends = [filters.SearchFilter]
    search_fields = ['in_evidence_start','publication__title']
    pagination_class = UniCmsApiPagination
    permission_classes = [IsAdminUser]
    serializer_class = PublicationContextSerializer

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        webpath_id = self.kwargs['webpath_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise Http404
        webpath = get_object_or_404(WebPath,
                                    pk=webpath_id,
                                    site=site)
        publications = PublicationContext.objects.filter(webpath=webpath)
        self.webpath = webpath
        is_active = self.request.GET.get('is_active')
        if is_active:
            publications = publications.filter(is_active=is_active)
        return publications

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get webpath
            webpath = serializer.validated_data.get('webpath')
            # check permissions on webpath
            permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                              user=request.user)
            publisher_perms = is_publisher(permission)
            if not publisher_perms:
                error_msg = _("You don't have permissions")
                return Response(error_msg, status=status.HTTP_403_FORBIDDEN)
            return super().post(request, *args, **kwargs)


class EditorWebpathPublicationContextView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PublicationContextSerializer
    error_msg = _("You don't have permissions")

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise Http404
        webpath_id = self.kwargs['webpath_id']
        pk = self.kwargs['pk']
        contexts = PublicationContext.objects.filter(pk=pk,
                                                     webpath__pk=webpath_id,
                                                     webpath__site__pk=site_id)
        return contexts

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            webpath = item.webpath
            permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                              user=request.user)
            publisher_perms = is_publisher(permission)
            if not publisher_perms:
                return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
            return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            webpath = item.webpath
            permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                              user=request.user)
            publisher_perms = is_publisher(permission)
            if not publisher_perms:
                return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        webpath = item.webpath
        permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                          user=request.user)
        publisher_perms = is_publisher(permission)
        if not publisher_perms:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
